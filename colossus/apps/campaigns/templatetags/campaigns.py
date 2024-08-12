from django import template
from django.utils.html import mark_safe

from ..constants import CampaignStatus

register = template.Library()


@register.filter
def campaign_status_badge(campaign):
    css_classes = {
        CampaignStatus.SENT: 'badge-success',
        CampaignStatus.SCHEDULED: 'badge-warning',
        CampaignStatus.DRAFT: 'badge-warning',
        CampaignStatus.QUEUED: 'badge-info',
        CampaignStatus.DELIVERING: 'badge-dark',
        CampaignStatus.PAUSED: 'badge-danger',
    }
    badge_class = css_classes[campaign.status]
    badge_text = campaign.get_status_display()
    html = '<span class="badge %s badge-pill">%s</span>' % (badge_class, badge_text)
    return mark_safe(html)
