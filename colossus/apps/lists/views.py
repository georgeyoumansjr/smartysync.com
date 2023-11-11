import datetime
from typing import Any, Dict

from django.db.models.query import QuerySet

from colossus.apps.subscribers.fields import MultipleEmailField

from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.forms import modelform_factory
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, DetailView, FormView, ListView, TemplateView,
    UpdateView, View,
)

from colossus.apps.core.models import Country
from colossus.apps.subscribers.constants import (
    ActivityTypes, Status, TemplateKeys, Workflows,
)
from colossus.apps.subscribers.models import (
    Activity, Subscriber, SubscriptionFormTemplate, Tag,
)
from colossus.apps.subscribers.subscription_settings import (
    SUBSCRIPTION_FORM_TEMPLATE_SETTINGS,
)
from colossus.utils import get_absolute_url, is_uuid

from .charts import (
    ListDomainsChart, ListLocationsChart, SubscriptionsSummaryChart,
)
from .forms import (
    BulkTagForm, ConfirmSubscriberImportForm, MailingListSMTPForm,
    PasteImportSubscribersForm, PasteSearchSubscribersForm, PasteDeleteSubscribersForm
)
from .mixins import FormTemplateMixin, MailingListMixin
from .models import MailingList, SubscriberImport
from .utils import get_non_existing_emails_and_return_list

from colossus.apps.campaigns.models import Campaign

def MailingListCampaignListView(request):
    context = {}
    mls_and_cmps = {}
    current_user = request.user
    campaigns = Campaign.objects.filter(created_by=current_user.id)
    mailinglists = MailingList.objects.filter(created_by=current_user.id)

    for mailinglist in mailinglists:
        mls_and_cmps[mailinglist.name] = campaigns.filter(mailing_list=mailinglist).values('name')
    
    context['mls_and_cmps'] = mls_and_cmps

    return render(request, 'lists/mailinglist_campaignlist.html', context)


@method_decorator(login_required, name='dispatch')
class MailingListListView(ListView):
    model = MailingList
    context_object_name = 'mailing_lists'
    ordering = ('name',)
    paginate_by = 25
    
    def get_context_data(self, **kwargs):
        kwargs['menu'] = 'lists'
        kwargs['total_count'] = MailingList.objects.count()
        return super().get_context_data(**kwargs)
    
    def get_queryset(self):
        current_user = self.request.user
        print(current_user)
        queryset = super().get_queryset().filter(created_by=current_user.id)
        print(queryset)
        return queryset
    
@method_decorator(login_required, name='dispatch')
class MailingListCreateView(CreateView):
    model = MailingList
    fields = ('name', 'slug', 'campaign_default_from_name', 'campaign_default_from_email', 'website_url')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['menu'] = 'lists'
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class MailingListDetailView(DetailView):
    model = MailingList
    context_object_name = 'mailing_list'

    def get_context_data(self, **kwargs) -> Dict:
        locations = self.object.get_active_subscribers() \
            .select_related('location') \
            .values('location__country__code', 'location__country__name') \
            .annotate(total=Count('location__country__code')) \
            .order_by('-total')[:10]

        last_campaign = self.object.campaigns.order_by('-send_date').first()

        domains = self.object.get_active_subscribers() \
            .select_related('domain') \
            .values('domain__name') \
            .annotate(total=Count('domain__name')) \
            .order_by('-total')[:10]

        thirty_days_ago = timezone.now() - datetime.timedelta(30)
        subscribed_expression = Count('id', filter=Q(activity_type=ActivityTypes.SUBSCRIBED))
        unsubscribed_expression = Count('id', filter=Q(activity_type=ActivityTypes.UNSUBSCRIBED))
        cleaned_expression = Count('id', filter=Q(activity_type=ActivityTypes.CLEANED))
        summary_last_30_days = Activity.objects \
            .filter(subscriber__mailing_list=self.object, date__gte=thirty_days_ago) \
            .aggregate(subscribed=subscribed_expression,
                       unsubscribed=unsubscribed_expression,
                       cleaned=cleaned_expression)

        kwargs['menu'] = 'lists'
        kwargs['submenu'] = 'details'
        kwargs['subscribed_count'] = self.object.subscribers.filter(status=Status.SUBSCRIBED).count()
        kwargs['unsubscribed_count'] = self.object.subscribers.filter(status=Status.UNSUBSCRIBED).count()
        kwargs['cleaned_count'] = self.object.subscribers.filter(status=Status.CLEANED).count()
        kwargs['locations'] = locations
        kwargs['last_campaign'] = last_campaign
        kwargs['summary_last_30_days'] = summary_last_30_days
        kwargs['domains'] = domains
        return super().get_context_data(**kwargs)
    
    def delete(self, request, *args, **kwargs):
        obj = self.object.delete()
        return super().delete(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class MailingListDeleteView(DeleteView):
    model = MailingList
    pk_url_kwarg = 'mailing_list'
    context_object_name = 'mailing_list'
    template_name = 'lists/mailing_list_confirm_delete.html'

    def get_success_url(self):
        return reverse('lists:lists')
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return self.model.objects.get(pk=pk)
    

@method_decorator(login_required, name='dispatch')
class MailingListCountryReportView(MailingListMixin, DetailView):
    model = MailingList
    context_object_name = 'mailing_list'
    template_name = 'lists/country_report.html'

    def get_context_data(self, **kwargs):
        country_code = self.kwargs.get('country_code')
        country = get_object_or_404(Country, code=country_code)
        country_total_subscribers = self.object.get_active_subscribers() \
            .filter(location__country__code=country_code) \
            .values('location__country__code') \
            .aggregate(total=Count('location__country__code'))
        cities = self.object.get_active_subscribers() \
                     .filter(location__country__code=country_code) \
                     .select_related('location') \
                     .values('location__name') \
                     .annotate(total=Count('location__name')) \
                     .order_by('-total')[:100]
        kwargs['menu'] = 'lists'
        kwargs['country'] = country
        kwargs['country_total_subscribers'] = country_total_subscribers['total']
        kwargs['cities'] = cities
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class SubscriberListView(MailingListMixin, ListView):
    model = Subscriber
    context_object_name = 'subscribers'
    paginate_by = 100
    template_name = 'lists/subscriber_list.html'

    def get_context_data(self, **kwargs):
        kwargs['submenu'] = 'subscribers'
        kwargs['total_count'] = self.model.objects.count()
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = self.model.objects.filter(mailing_list_id=self.kwargs.get('pk'))

        tags_filter = self.request.GET.getlist('tags__in')
        if tags_filter:
            queryset = queryset.filter(tags__in=tags_filter)

        if self.request.GET.get('q', ''):
            query = self.request.GET.get('q').strip()

            if is_uuid(query):
                queryset = queryset.filter(uuid=query)
            else:
                queryset = queryset.filter(Q(email__icontains=query) | Q(name__icontains=query))

            self.extra_context = {
                'is_filtered': True,
                'query': query
            }

        return queryset.order_by('optin_date')
    
    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        delete = request.POST.get('delete', False)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="emails.txt"'
        for q in queryset:
            response.write(q)
            response.write('\n')
            print(q)

        if delete:
             queryset.delete()
        return response
        super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()

        return super().delete(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class SubscriberCreateView(MailingListMixin, CreateView):
    model = Subscriber
    fields = ('email', 'name')
    template_name = 'lists/subscriber_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.mailing_list_id = self.kwargs.get('pk')
        self.object.status = Status.SUBSCRIBED
        self.object.save()
        return redirect('lists:subscribers', pk=self.kwargs.get('pk'))


@method_decorator(login_required, name='dispatch')
class SubscriberDetailView(MailingListMixin, DetailView):
    model = Subscriber
    pk_url_kwarg = 'subscriber_pk'
    template_name = 'lists/subscriber_detail.html'
    context_object_name = 'subscriber'


@method_decorator(login_required, name='dispatch')
class SubscriberUpdateView(MailingListMixin, UpdateView):
    model = Subscriber
    fields = '__all__'
    pk_url_kwarg = 'subscriber_pk'
    template_name = 'lists/subscriber_form.html'

    def get_success_url(self):
        return reverse('lists:subscribers', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class SubscriberDeleteView(MailingListMixin, DeleteView):
    model = Subscriber
    pk_url_kwarg = 'subscriber_pk'
    context_object_name = 'subscriber'
    template_name = 'lists/subscriber_confirm_delete.html'

    def get_success_url(self):
        return reverse('lists:subscribers', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class ImportSubscribersView(MailingListMixin, TemplateView):
    template_name = 'lists/import_subscribers.html'

    def get_context_data(self, **kwargs):
        kwargs['submenu'] = 'subscribers'
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class PasteEmailsImportSubscribersView(MailingListMixin, FormView):
    template_name = 'lists/import_subscribers_form.html'
    form_class = PasteImportSubscribersForm
    extra_context = {'title': _('Paste Emails')}

    def form_valid(self, form):
        try:
            mailing_list_id = self.kwargs.get('pk')
            mailing_list = MailingList.objects.only('pk').get(pk=mailing_list_id)
            form.import_subscribers(mailing_list)
            return redirect('lists:subscribers', pk=mailing_list_id)
        except MailingList.DoesNotExist:
            raise Http404
        
@method_decorator(login_required, name='dispatch')
class PasteEmailsSearchSubscribersView(FormView):
    template_name = 'lists/mailinglist_email.html'
    form_class = PasteSearchSubscribersForm
    extra_context = {'title': _('Paste Emails')}

    def form_valid(self, form):
        context = {}
        campaign_subscribers, multiple_campaign_subscribers, alone_subscribers, multiple_campaign_subscribers_all = form.search_subscribers()
        if len(campaign_subscribers) != 0:
            context['campaign_subscribers'] = campaign_subscribers
        if len(multiple_campaign_subscribers):
            context['multiple_campaign_subscribers'] = multiple_campaign_subscribers
        if len(alone_subscribers):
            context['alone_subscribers'] = alone_subscribers
        if len(multiple_campaign_subscribers_all):
            context['multiple_campaign_subscribers_all'] = multiple_campaign_subscribers_all

        return render( self.request, 'lists/mailinglist_email.html', context )
    
    def get(self, request):

        return super().get(request)
    
@method_decorator(login_required, name='dispatch')
class PasteEmailsDeleteSubscribersView(FormView):
    template_name = 'lists/delete_subscribers.html'
    form_class = PasteDeleteSubscribersForm 
    extra_context = {'title': _('Paste Emails')}

    def form_valid(self, form):
        form.delete_subscribers()
        return redirect('lists:lists')


@method_decorator(login_required, name='dispatch')
class SubscriptionFormsView(MailingListMixin, TemplateView):
    template_name = 'lists/subscription_forms.html'

    def get_context_data(self, **kwargs):
        kwargs['submenu'] = 'forms'
        kwargs['sub'] = get_absolute_url('subscribers:subscribe', {'mailing_list_uuid': self.mailing_list.uuid})
        kwargs['sub_short'] = get_absolute_url('subscribe_shortcut', {'mailing_list_slug': self.mailing_list.slug})
        kwargs['unsub'] = get_absolute_url('subscribers:unsubscribe_manual', {
            'mailing_list_uuid': self.mailing_list.uuid
        })
        kwargs['unsub_short'] = get_absolute_url('unsubscribe_shortcut', {'mailing_list_slug': self.mailing_list.slug})
        return super().get_context_data(**kwargs)


class TagMixin:
    model = Tag
    extra_context = {'submenu': 'tags'}
    pk_url_kwarg = 'tag_pk'

    def get_queryset(self):
        return super().get_queryset().filter(mailing_list_id=self.kwargs.get('pk'))


@method_decorator(login_required, name='dispatch')
class TagListView(TagMixin, MailingListMixin, ListView):
    context_object_name = 'tags'
    paginate_by = 100
    template_name = 'lists/tag_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.GET.get('q', ''):
            query = self.request.GET.get('q').strip()
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
            self.extra_context = {
                'is_filtered': True,
                'query': query
            }

        queryset = queryset.annotate(subscribers_count=Count('subscribers'))
        return queryset.order_by('name')


class BulkTagSubscribersView(LoginRequiredMixin, TagMixin, MailingListMixin, FormView):
    form_class = BulkTagForm
    context_object_name = 'tag'
    template_name = 'lists/bulk_tag_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['mailing_list'] = self.mailing_list
        return kwargs

    def form_valid(self, form):
        form.tag_subscribers()
        return redirect('lists:tags', pk=self.mailing_list.pk)


@method_decorator(login_required, name='dispatch')
class TagCreateView(TagMixin, MailingListMixin, CreateView):
    fields = ('name', 'description')
    context_object_name = 'tag'
    template_name = 'lists/tag_form.html'

    def form_valid(self, form):
        tag = form.save(commit=False)
        tag.mailing_list_id = self.kwargs.get('pk')
        tag.save()
        messages.success(self.request, _('Tag "%(name)s" created with success.') % form.cleaned_data)
        return redirect('lists:tags', pk=self.kwargs.get('pk'))


@method_decorator(login_required, name='dispatch')
class TagUpdateView(SuccessMessageMixin, TagMixin, MailingListMixin, UpdateView):
    fields = ('name', 'description')
    context_object_name = 'tag'
    template_name = 'lists/tag_form.html'
    success_message = _('Tag "%(name)s" updated with success.')

    def get_success_url(self):
        return reverse('lists:tags', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class TagDeleteView(TagMixin, MailingListMixin, DeleteView):
    context_object_name = 'tag'
    template_name = 'lists/tag_confirm_delete.html'

    def get_success_url(self):
        return reverse('lists:tags', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class AbstractSettingsView(UpdateView):
    model = MailingList
    context_object_name = 'mailing_list'
    template_name = 'lists/settings.html'

    def get_context_data(self, **kwargs):
        kwargs['menu'] = 'lists'
        kwargs['submenu'] = 'settings'
        kwargs['subsubmenu'] = self.subsubmenu
        kwargs['title'] = self.title
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse(self.success_url_name, kwargs={'pk': self.kwargs.get('pk')})


class ListSettingsView(AbstractSettingsView):
    fields = ('name', 'slug', 'website_url', 'contact_email_address',)
    success_url_name = 'lists:settings'
    subsubmenu = 'list_settings'
    title = _('Settings')


class SubscriptionSettingsView(AbstractSettingsView):
    fields = ('list_manager', 'enable_recaptcha', 'recaptcha_site_key', 'recaptcha_secret_key')
    success_url_name = 'lists:subscription_settings'
    subsubmenu = 'subscription_settings'
    title = _('Subscription settings')


class CampaignDefaultsView(AbstractSettingsView):
    fields = ('campaign_default_from_name', 'campaign_default_from_email', 'campaign_default_email_subject',)
    success_url_name = 'lists:defaults'
    subsubmenu = 'defaults'
    title = _('Campaign defaults')


class SMTPCredentialsView(AbstractSettingsView):
    form_class = MailingListSMTPForm
    success_url_name = 'lists:smtp'
    subsubmenu = 'smtp'
    title = _('SMTP credentials')


@method_decorator(login_required, name='dispatch')
class FormsEditorView(MailingListMixin, TemplateView):
    template_name = 'lists/forms_editor.html'

    def get_context_data(self, **kwargs):
        kwargs['template_keys'] = TemplateKeys
        kwargs['workflows'] = Workflows
        kwargs['subscription_forms'] = SUBSCRIPTION_FORM_TEMPLATE_SETTINGS
        return super().get_context_data(**kwargs)


@method_decorator(login_required, name='dispatch')
class SubscriptionFormTemplateUpdateView(FormTemplateMixin, MailingListMixin, UpdateView):
    model = SubscriptionFormTemplate
    context_object_name = 'form_template'
    template_name = 'lists/form_template_form.html'

    def get_success_url(self):
        return reverse('lists:edit_form_template', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        kwargs['template_keys'] = TemplateKeys
        kwargs['workflows'] = Workflows
        kwargs['subscription_forms'] = SUBSCRIPTION_FORM_TEMPLATE_SETTINGS
        return super().get_context_data(**kwargs)

    def get_form_class(self):
        fields = self.object.settings['fields']
        form_class = modelform_factory(self.model, fields=fields)
        return form_class


@method_decorator(login_required, name='dispatch')
class ResetFormTemplateView(FormTemplateMixin, MailingListMixin, View):
    def post(self, request: HttpRequest, pk: int, form_key: str):
        form_template = self.get_object()
        form_template.load_defaults()
        messages.success(request, gettext('Default template restored with success!'))
        return redirect('lists:edit_form_template', pk=pk, form_key=form_key)


@method_decorator(login_required, name='dispatch')
class PreviewFormTemplateView(FormTemplateMixin, MailingListMixin, View):
    def post(self, request, pk, form_key):
        self.form_template = self.get_object()
        content = request.POST.get('content_html')
        html = self.form_template.render_template({'content': content, 'preview': True})
        return HttpResponse(html)

    def get(self, request, pk, form_key):
        self.form_template = self.get_object()
        html = self.form_template.render_template({'preview': True})
        return HttpResponse(html)


@method_decorator(login_required, name='dispatch')
class CustomizeDesignView(UpdateView):
    model = MailingList
    fields = ('forms_custom_css', 'forms_custom_header')
    context_object_name = 'mailing_list'
    template_name = 'lists/customize_design.html'

    def get_context_data(self, **kwargs):
        kwargs['menu'] = 'lists'
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('lists:forms_editor', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class SubscriberImportView(MailingListMixin, CreateView):
    model = SubscriberImport
    fields = ('file',)
    template_name = 'lists/import_subscribers_form.html'
    extra_context = {'title': _('Import CSV File')}

    def get_context_data(self, **kwargs):
        kwargs['subscriber_imports'] = SubscriberImport.objects.order_by('-upload_date')
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        mailing_list_id = self.kwargs.get('pk')
        subscriber_import = form.save(commit=False)
        subscriber_import.user = self.request.user
        subscriber_import.mailing_list_id = mailing_list_id
        subscriber_import.save()
        subscriber_import.set_size()
        return redirect('lists:import_preview', pk=mailing_list_id, import_pk=subscriber_import.pk)


@method_decorator(login_required, name='dispatch')
class SubscriberImportPreviewView(MailingListMixin, UpdateView):
    model = SubscriberImport
    form_class = ConfirmSubscriberImportForm
    template_name = 'lists/import_preview.html'
    pk_url_kwarg = 'import_pk'
    context_object_name = 'subscriber_import'

    def get_success_url(self):
        submit = self.request.POST.get('submit', 'save')
        if submit == 'import':
            return reverse('lists:import_queued', kwargs=self.kwargs)
        return reverse('lists:csv_import_subscribers', kwargs={'pk': self.kwargs.get('pk')})


@method_decorator(login_required, name='dispatch')
class SubscriberImportQueuedView(MailingListMixin, DetailView):
    model = SubscriberImport
    template_name = 'lists/import_queued.html'
    pk_url_kwarg = 'import_pk'
    context_object_name = 'subscriber_import'


@method_decorator(login_required, name='dispatch')
class SubscriberImportDeleteView(MailingListMixin, DeleteView):
    model = SubscriberImport
    pk_url_kwarg = 'import_pk'
    context_object_name = 'subscriber_import'
    template_name = 'lists/subscriber_import_confirm_delete.html'

    def get_success_url(self):
        return reverse('lists:csv_import_subscribers', kwargs={'pk': self.kwargs.get('pk')})


class ChartView(View):
    chart_class: Any

    def get(self, request, pk):
        try:
            mailing_list = MailingList.objects.get(pk=pk)
            chart = self.chart_class(mailing_list)
            return JsonResponse({'chart': chart.get_settings()})
        except MailingList.DoesNotExist:
            # bad request status code
            return JsonResponse(data={'message': gettext('Invalid mailing list id.')}, status_code=400)


@method_decorator(login_required, name='dispatch')
class SubscriptionsSummaryChartView(ChartView):
    chart_class = SubscriptionsSummaryChart


@method_decorator(login_required, name='dispatch')
class ListDomainsChartView(ChartView):
    chart_class = ListDomainsChart


@method_decorator(login_required, name='dispatch')
class ListLocationsChartView(ChartView):
    chart_class = ListLocationsChart


@login_required
def download_subscriber_import(request, pk, import_pk):
    subscriber_import = get_object_or_404(SubscriberImport, pk=import_pk, mailing_list_id=pk)
    filename = subscriber_import.file.name.split('/')[-1]
    response = HttpResponse(subscriber_import.file.read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response

from django.shortcuts import render
@login_required
def search_subscribers(request):
    context = {}


    emails = MultipleEmailField(
        label=_('Paste email addresses'),
        help_text=_('One email per line, or separated by comma. Duplicate emails will be suppressed.'),
    )

    with transaction.atomic():
        for email in emails:

            try:
                subscriber = Subscriber.objects.get( email__iexact=email )
                if not subscriber.mailing_list.name in mailing_lists:
                    mailing_lists[subscriber.mailing_list.name] = [email]
                (mailing_lists[subscriber.mailing_list.name]).append(email)
            except Subscriber.DoesNotExist:
                continue
    return HttpResponse( render(request, 'search_subscribers.html', context) )

@login_required
def delete_non_existing_subscribers(request):
    emails = get_non_existing_emails_and_return_list()
    for email in emails:
        subscriber_to_delete = Subscriber.objects.filter(email=email)
        if subscriber_to_delete.exists():
            subscriber_to_delete.delete()
    mailing_lists = MailingList.objects.all()
    for mailing_list in mailing_lists:
        mailing_list.update_subscribers_count()
    return redirect('lists:lists')

def delete_duplicate_subscribers(request):
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        if subscriber.email == 'coboaccess@gmail.com' or subscriber.email == 'georgeyoumansjr@gmail.com':
            continue
        subs = subscribers.filter(email=subscriber.email)
        if subs.count() > 1:
            obj = subs.order_by('optin_date').first()
            objects_to_delete = subs.filter(optin_date__gt=obj.optin_date)
            objects_to_delete.delete()

    mailing_lists = MailingList.objects.all()
    for mailing_list in mailing_lists:
        mailing_list.update_subscribers_count()
    return redirect('lists:lists')
