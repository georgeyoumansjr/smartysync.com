import os
from django.db import models
from django.conf import settings

from django.utils.translation import gettext, gettext_lazy as _

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
    
