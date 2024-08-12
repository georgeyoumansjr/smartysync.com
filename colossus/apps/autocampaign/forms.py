from django import forms
import os
from django.conf import settings
from .models import AutoCampaign
from colossus.apps.campaigns.models import Campaign
from colossus.apps.lists.models import MailingList


def get_pdf_files():
    pdf_path = os.path.join(settings.STATIC_ROOT, 'PDFs')
    if not os.path.exists(pdf_path):
        return []
    return [(f, f) for f in os.listdir(pdf_path) if f.endswith('.pdf')]


class AutoCampaignForm(forms.ModelForm):
    pdf_file = forms.ChoiceField(choices=[], required=False)
    
    class Meta:
        model = AutoCampaign
        fields = ['campaign', 'mailing_list', 'mail_numbers', 'pdf_file']
        verbose_name = 'Auto Campaign'
        verbose_name_plural = 'Auto Campaigns'
        
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['campaign'].queryset = Campaign.objects.filter(created_by=user.id, status= 1).exclude(name__icontains="(copy)").order_by('name')
        self.fields['mailing_list'].queryset = MailingList.objects.filter(created_by=user.id).exclude(name__icontains="AUTO PT").order_by('name')
        
        pdf_choices = [("", "None")] + get_pdf_files()
        self.fields['pdf_file'].choices = pdf_choices
        self.fields['pdf_file'].initial = ""  # Ensure no PDF file is selected by default

class ConfirmSendForm(forms.Form):
    confirm = forms.BooleanField(required=True, initial=False, label='I confirm that I want to send this campaign')