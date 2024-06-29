import os
from django.db import models
from django.conf import settings

from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.accounts.models import User
from django.urls import reverse
from django.utils import timezone

from colossus.apps.campaigns.models import Campaign
from colossus.apps.lists.models import MailingList
# Create your models here.


from django.core.exceptions import ValidationError

def validate_positive(value):
    if value <= 0:
        raise ValidationError(
            '%(value)s is not a positive integer greater than 0',
            params={'value': value},
        )



def get_pdf_files():
    pdf_path = os.path.join(settings.STATIC_ROOT, 'PDFs')
    if not os.path.exists(pdf_path):
        return []
    return [(f, f) for f in os.listdir(pdf_path) if f.endswith('.pdf')]


class AutoCampaign(models.Model):

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        # ('scheduled', _('Scheduled')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
    ]
    
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        verbose_name=_('campaign'),
        related_name='auto_campaigns',
        null=True,
        blank=True
    )
    
    mailing_list = models.ForeignKey(
        MailingList,
        on_delete=models.SET_NULL,
        verbose_name=_('mailing list'),
        related_name='auto_campaigns',
        null=True,
        blank=True
    )

    mail_numbers = models.PositiveIntegerField(
        validators=[validate_positive],
        verbose_name=_("mail numbers"),
        default=50,
        null=False,
    )
    
    pdf_file = models.CharField(
        max_length=255,
        choices=get_pdf_files(),
        verbose_name=_('PDF file')
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('status')
    )
    
    create_date = models.DateTimeField(_('create date'), auto_now_add=True)
    update_date = models.DateTimeField(_('update date'), default=timezone.now)

    send_date = models.DateTimeField(_('send date'), null=True, blank=True, db_index=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name=_('created by'),
        related_name='auto_created_campaigns',
        null=True,
        blank=True
    )
    
    
    def get_absolute_url(self) -> str:
        if self.status in ["draft", "sent"]:
            return reverse('autocampaign:autocampaign_detail', kwargs={'pk': self.pk})
        # elif self.is_scheduled:
        #     return reverse('campaigns:campaign_scheduled', kwargs={'pk': self.pk})
        return reverse('autocampaign:campaign_list')


    def is_draft(self):
        return self.status == 'draft'
    
    # def is_scheduled(self):
    #     return self.status == 'scheduled'
    
    def is_sent(self):
        return self.status == 'sent'
    
    def is_failed(self):
        return self.status == 'failed'
