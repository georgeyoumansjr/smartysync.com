from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from colossus.apps.accounts.forms import AdminUserCreationForm
from colossus.apps.campaigns.constants import CampaignStatus
from colossus.apps.campaigns.models import Campaign
from colossus.apps.lists.models import MailingList
from colossus.apps.subscribers.constants import ActivityTypes
from colossus.apps.subscribers.models import Activity, Subscriber

import datetime

User = get_user_model()


@method_decorator(login_required, name='dispatch')
class SiteUpdateView(UpdateView):
    model = Site
    fields = ('name', 'domain',)
    template_name = 'core/site_form.html'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return Site.objects.get(pk=django_settings.SITE_ID)


def home(request):

    return render(request, 'core/home.html', {
        'menu': 'dashboard',
    })

@login_required
def dashboard(request):
    current_user = request.user
    drafts = Campaign.objects.filter(status=CampaignStatus.DRAFT,created_by=current_user.id)
    sent = Campaign.objects.filter(status=CampaignStatus.SENT,created_by=current_user.id).count()
    oneMonthAgo = datetime.date.today() - datetime.timedelta(weeks=4)

    subscriberActivities = Activity.objects \
        .select_related('subscriber__mailing_list') \
        .filter(activity_type__in={ActivityTypes.SUBSCRIBED, ActivityTypes.UNSUBSCRIBED}, date__gte=oneMonthAgo) \
        .filter(campaign__created_by=current_user.id)
    
    
    campaignOpens = Activity.objects \
        .filter(activity_type=ActivityTypes.OPENED)\
        .filter(campaign__created_by=current_user.id).count()
    
    subbed = subscriberActivities.filter(activity_type=ActivityTypes.SUBSCRIBED)
    unsubbed = subscriberActivities.filter(activity_type=ActivityTypes.UNSUBSCRIBED)
    subDelta = subbed.count() - unsubbed.count()

    
    subscribers = Subscriber.objects.select_related('mailing_list').filter(mailing_list__created_by=current_user.id).order_by('optin_date')
    sub_list = []
    for sub in subscribers:
        if not sub.email in sub_list:
            sub_list.append(sub.email)
    totalSubCount = len(sub_list)    

    activities = Activity.objects \
        .select_related('campaign', 'subscriber__mailing_list') \
        .filter(activity_type__in={ActivityTypes.SUBSCRIBED, ActivityTypes.UNSUBSCRIBED}) \
        .filter(campaign__created_by=current_user.id) \
        .order_by('-date')[:50]
    
    # Chart Data
    # Subscribers
    chartData = {'date':[], 'subCount':[], 'campaignCount':[]}
    campaigns = Campaign.objects.filter(status=CampaignStatus.SENT,created_by=current_user.id).order_by('send_date')
    try:
        firstDate = subscribers.first().optin_date if subscribers.first().optin_date < campaigns.first().send_date else campaigns.first().send_date
        lastDate  = subscribers.last().optin_date if subscribers.last().optin_date > campaigns.last().send_date else campaigns.last().send_date
        # lastDate = subscribers.last().optin_date
        dateDelta = ( lastDate - firstDate ) / 7
        endDate = firstDate + dateDelta
        for i in range(7):
            subCount = subscribers.filter( optin_date__lte=endDate).count()
            campaignCount = campaigns.filter( send_date__lte=endDate).count()
            chartData['date'].append(endDate.strftime("%m/%d/%Y"))
            chartData['subCount'].append(subCount)
            chartData['campaignCount'].append(campaignCount)
            endDate += dateDelta
    except AttributeError:
        return render(request,'core/alternate_dashboard.html')
    
    
    return render(request, 'core/dashboard.html', {
        'menu': 'dashboard',
        'campaignOpens': campaignOpens,
        'activities': activities,
        'drafts': drafts,
        'sent': sent,
        'subbed': subbed,
        'unsubbed': unsubbed,
        'subDelta': subDelta,
        'totalSubCount': totalSubCount,
        'chartData': chartData,
    })


def setup(request):
    # if User.objects.exists() or MailingList.objects.exists():
    #     return redirect('dashboard')

    site = Site.objects.get(pk=django_settings.SITE_ID)
    if site.domain == 'example.com':
        site.name = 'Colossus'
        site.domain = request.META.get('HTTP_HOST')
        site.save()
    return redirect('setup_account')


def setup_account(request):
    # if User.objects.exists() or MailingList.objects.exists():
    #     return redirect('dashboard')

    if request.method == 'POST':
        form = AdminUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Account created with success! Go ahead and create your first mailing list.'))
            return redirect('lists:new_list')
    else:
        form = AdminUserCreationForm()
    return render(request, 'core/setup_account.html', {'form': form})


def subscribe_shortcut(request, mailing_list_slug):
    mailing_list = get_object_or_404(MailingList, slug=mailing_list_slug)
    return redirect('subscribers:subscribe', mailing_list_uuid=mailing_list.uuid)


def unsubscribe_shortcut(request, mailing_list_slug):
    mailing_list = get_object_or_404(MailingList, slug=mailing_list_slug)
    return redirect('subscribers:unsubscribe_manual', mailing_list_uuid=mailing_list.uuid)
