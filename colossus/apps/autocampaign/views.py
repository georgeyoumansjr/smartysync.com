from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import ContextMixin


from .models import AutoCampaign
from .forms import AutoCampaignForm

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
        
        # if self.request.GET.get('q', ''):
        #     query = self.request.GET.get('q')
        #     queryset = queryset.filter(name__icontains=query)
        #     self.extra_context['is_filtered'] = True
        #     self.extra_context['query'] = query

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
    