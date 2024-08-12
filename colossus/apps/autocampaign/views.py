from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, DetailView
from django.views.generic.base import ContextMixin
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.lists.constants import ImportFields, ImportStatus
from colossus.apps.lists.tasks import import_subscribers
from colossus.apps.subscribers.constants import ActivityTypes, Status
from colossus.apps.subscribers.fields import MultipleEmailField
from colossus.apps.subscribers.models import Domain, Subscriber, Tag
from colossus.apps.accounts.models import User

from colossus.apps.lists.models import MailingList, SubscriberImport

from colossus.apps.campaigns.models import Campaign
from colossus.apps.campaigns.constants import CampaignStatus


from .models import AutoCampaign
from .forms import AutoCampaignForm, ConfirmSendForm

class AutoCampaignMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        kwargs['menu'] = 'autocampaigns'
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class AutoCampaignListView(AutoCampaignMixin, ListView):
    model = AutoCampaign
    context_object_name = 'autocampaigns'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        kwargs['total_count'] = AutoCampaign.objects.count()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.extra_context = {}
        current_user = self.request.user
        queryset = super().get_queryset().filter(created_by=current_user.id).select_related('mailing_list')
        
        if self.request.GET.get('q', ''):
            query = self.request.GET.get('q')
            queryset = queryset.filter(campaign__name__icontains=query)
            self.extra_context['is_filtered'] = True
            self.extra_context['query'] = query

        queryset = queryset.order_by('-update_date')

        return queryset





@method_decorator(login_required, name='dispatch')
class AutoCampaignCreateView(AutoCampaignMixin, CreateView):
    model = AutoCampaign
    # context_object_name = 'auto_campaign'
    form_class = AutoCampaignForm
    # template_name = 'autocampaign/autocampaign_create.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        print(form.instance)
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    

@method_decorator(login_required, name='dispatch')
class AutoCampaignEditView(AutoCampaignMixin, UpdateView):
    model = AutoCampaign
    form_class = AutoCampaignForm
    template_name = 'autocampaign/autocampaign_form.html'  # Use the same template as the create view

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != 'draft':
            # Redirect to the detail view or raise a permission denied error
            return redirect('autocampaign:autocampaign_detail', pk=self.object.pk)
            # Alternatively, raise PermissionDenied
            # raise PermissionDenied("You cannot edit a campaign that is not in draft status.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user  # Assuming you have an updated_by field
        print(form.instance)
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

@method_decorator(login_required, name='dispatch')
class AutoCampaignDetailView(AutoCampaignMixin, DetailView):
    model = AutoCampaign
    context_object_name = 'autocampaign'
    extra_context = {'submenu': 'details'}


@method_decorator(login_required, name='dispatch')
class AutoCampaignDeleteView(AutoCampaignMixin, DeleteView):
    model = AutoCampaign
    context_object_name = 'autocampaign'
    success_url = reverse_lazy('autocampaign:autocampaign_list')


@login_required
def confim_send(request,pk):
    autocampaign = get_object_or_404(AutoCampaign, pk=pk)
    user = request.user
    if request.method == 'POST':
        form = ConfirmSendForm(request.POST)
        if form.is_valid():
            source_mailing_list_name = autocampaign.mailing_list.name
            max_number_of_emails = autocampaign.mail_numbers
            pdf_name = autocampaign.pdf_file
            try:
                campaign = autocampaign.campaign

            except Campaign.DoesNotExist:
                print('No campaign. Set the campaign first')
                messages.error(request, 'No campaign found. Set the campaign first.')
                return redirect(reverse('autocampaign:autocampaign_detail', kwargs={'pk': pk}))
                

            try:
                source_mailing_list = MailingList.objects.only('pk').get(created_by=user,name=source_mailing_list_name)

            except MailingList.DoesNotExist:
                print(f'No mailing list to get the emails from. Create the mailing list with the name : {source_mailing_list_name}')
                messages.error(request, f'No mailing list to get the emails from. Create the mailing list with the name: {source_mailing_list_name}')
                return redirect(reverse('autocampaign:autocampaign_detail', kwargs={'pk': pk}))


            emails = []

            # test the adding next batch if current one has more than 500 emails
            # for i in range(400):  
            #     emails.append(f'{uuid.uuid4()}@gmail.com')

            counter = 0

            for subscriber in source_mailing_list.subscribers.all():
                if Subscriber.objects.filter(mailing_list__name__startswith=f'{source_mailing_list_name} AUTO',
                                            email=subscriber.email).exists():
                    continue
                emails.append(subscriber.email)
                counter += 1

                print(f"Email {counter}: {subscriber.email}")

                if counter == max_number_of_emails:
                    print(f"Max number of emails is {max_number_of_emails}.")
                    break

            print(f'Collected {counter} emails.')

            if counter == 0:
                print('No emails to send. Either script is done with the current set of emails or there is a problem with the logic.')
                print(f'Source mailing list name : {source_mailing_list_name}')
                print(f'Source mailing list subscriber count : {source_mailing_list.subscribers_count}')
                
                if source_mailing_list.subscribers_count == 0:
                    print('Source mailing list is empty. Please make sure it\'s the right mailing list.')

                prefix = f'{source_mailing_list_name} AUTO'
                existing_mailing_lists_with_prefix = MailingList.objects.filter(name__startswith=prefix)
                print(f"Existing mailing lists with prefix {prefix} : ")

                if not existing_mailing_lists_with_prefix.exists():
                    print('None')
                for m in existing_mailing_lists_with_prefix:
                    print(f'Name : {m.name}')
                    print(f'Subscriber Count : {m.subscribers_count}')

                messages.error(request, f'No emails left to send campaign to. Switch the mailing list')
                return redirect(reverse('autocampaign:autocampaign_detail', kwargs={'pk': pk}))


                

            try:
                i = 1
                while True:
                    batch_mailing_list_name = f'{source_mailing_list_name} AUTO PT-{i}'
                    batch_mailing_list = MailingList.objects.get(created_by=user, name=batch_mailing_list_name)

                    i += 1
                    continue

            except MailingList.DoesNotExist:
                batch_mailing_list = MailingList.objects.create(
                    created_by=user, 
                    name = batch_mailing_list_name,
                    slug = batch_mailing_list_name.lower(),
                    contact_email_address = 'coboaccess@gmail.com',
                    website_url = 'https://thetitandev.com',
                    campaign_default_from_name = 'Ger Wholesale',
                    campaign_default_from_email = 'contact@gerwholesalers.com',
                    campaign_default_email_subject = 'Ger Wholesale',
                )
            

            
            if 'georgeyoumansjr@gmail.com' not in emails:
                emails.append('georgeyoumansjr@gmail.com')

            if 'coboaccess@gmail.com' not in emails:
                emails.append('coboaccess@gmail.com')

            if 'coboaccess3@gmail.com' not in emails:
                emails.append('coboaccess3@gmail.com')

            cached_domains = dict()
            status = 2  # SUBSCRIBED

            with transaction.atomic():
                for email in emails:
                    email_name, domain_part = email.rsplit('@', 1)
                    domain_name = '@' + domain_part

                    try:
                        domain = cached_domains[domain_name]
                    except KeyError:
                        domain, created = Domain.objects.get_or_create(name=domain_name)
                        cached_domains[domain_name] = domain

                    print(email)
                    
                    subscriber, created = Subscriber.objects.get_or_create(
                        email__iexact=email,
                        mailing_list=batch_mailing_list,
                        defaults={
                            'email': email,
                            'domain': domain
                        }
                    )

                    # georgeyoumansjr and coboaccess sent activity for this campaign should be removed
                    # or else it won't send the email to them
                    activity = subscriber.activities.filter(activity_type=ActivityTypes.SENT, email=campaign.email)
                    if activity.exists():
                        activity.delete()


                    if created:
                        subscriber.create_activity(ActivityTypes.IMPORTED)
                    subscriber.status = status
                    subscriber.update_date = timezone.now()
                    subscriber.save()
                batch_mailing_list.update_subscribers_count()

            campaign.mailing_list = batch_mailing_list
            campaign.status = CampaignStatus.QUEUED  # it might be in SENT state in which case campaign won't be send again
            campaign.save()


            if pdf_name:  # send with attachment
                print('PDF name is :' + pdf_name)
                pdf_path = settings.STATIC_ROOT + '/PDFs/' + pdf_name
                campaign.send(pdf_name=pdf_name, pdf_path=pdf_path)

            else:  
                campaign.send()

            autocampaign.status = 'sent'
            autocampaign.send_date = timezone.now()
            autocampaign.save()
            messages.success(request, 'Campaign is successfully being sent.')
            return redirect(reverse('autocampaign:autocampaign_detail', kwargs={'pk': pk}))
    else:
        form = ConfirmSendForm()

    context = {
        'autocampaign': autocampaign,
        'form': form,
    }
    return render(request, 'autocampaign/autocampaign_confirm_send.html', context)




