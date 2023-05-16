from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, get_connection
from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext
from django.template.loader import render_to_string

from colossus.utils import get_client_ip
from colossus.apps.campaigns.api import send_campaign

from .constants import Status
from .models import Domain, Subscriber

import logging

logger = logging.getLogger(__name__)
logger.setLevel('INFO')

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.mailing_list = kwargs.pop('mailing_list')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        is_subscribed = Subscriber.objects \
            .filter(email__iexact=email, status=Status.SUBSCRIBED, mailing_list=self.mailing_list) \
            .exists()
        if is_subscribed:
            email_validation_error = ValidationError(
                gettext('The email address "%(email)s" is already subscribed to this list.'),
                params={'email': email},
                code='already_subscribed_error'
            )
            self.add_error('email', email_validation_error)
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return Subscriber.objects.normalize_email(email)

    @transaction.atomic
    def subscribe(self, request):
        email = self.cleaned_data.get('email')

        email_name, domain_part = email.rsplit('@', 1)
        domain_name = '@' + domain_part
        email_domain, created = Domain.objects.get_or_create(name=domain_name)

        subscriber, created = Subscriber.objects.get_or_create(email=email, mailing_list=self.mailing_list, defaults={
            'domain': email_domain
        })
        subscriber.status = Status.PENDING
        subscriber.optin_ip_address = get_client_ip(request)
        subscriber.optin_date = timezone.now()
        subscriber.save()

        if not created:
            subscriber.tokens.filter(description='confirm_subscription').delete()
            return subscriber

        token = subscriber.tokens.create(description='confirm_subscription')
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        domain = current_site.domain
        path = reverse('subscribers:confirm_double_optin_token', kwargs={
            'mailing_list_uuid': self.mailing_list.uuid,
            'token': token.text
        })
        confirm_link = '%s://%s%s' % (protocol, domain, path)

        confirm_email = self.mailing_list.get_confirm_email_template()
        confirm_email.send(subscriber.get_email(), {
            'confirm_link': confirm_link
        })

        with get_connection() as connection:
            if isinstance(email, str):
                email = [email,]

            #subject = 'Thank you for subscribing'
            subject = '🍚 Your 10 Delicious Rice Recipes are attached below!'
            from_email = None
    
            html_message = render_to_string('subscribers/email_to_send.html')

            email_to_send = EmailMessage(
                    subject=subject,
                    body=html_message,
                    from_email=from_email,
                    to=email,
                    connection=connection
            )
            
            email_to_send.content_subtype = 'html'
            try:
                email_to_send.send(fail_silently=False)
            except Exception as e:
                logger.exception(f'Could not send the email to {email} due to following error:', e)

        

        return subscriber


class UnsubscribeForm(forms.Form):
    email = forms.EmailField()

    class Meta:
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.mailing_list = kwargs.pop('mailing_list')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        is_subscribed = Subscriber.objects.filter(
            email__iexact=email,
            mailing_list=self.mailing_list,
            status=Status.SUBSCRIBED
        )
        if not is_subscribed:
            email_validation_error = ValidationError(
                gettext('The email address "%(email)s" is not subscribed to this list.'),
                params={'email': email},
                code='not_subscribed_error'
            )
            self.add_error('email', email_validation_error)
        return cleaned_data

    def unsubscribe(self, request):
        email = self.cleaned_data.get('email')
        subscriber = Subscriber.objects.get(email=email, mailing_list=self.mailing_list)
        subscriber.unsubscribe(request)
