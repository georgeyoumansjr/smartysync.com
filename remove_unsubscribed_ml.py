import os 
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime


from dotenv import load_dotenv 
from django.conf import settings


from typing import Dict, List

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail.backends.smtp import EmailBackend
from django.db import transaction
from django.forms import BoundField
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.lists.constants import ImportFields, ImportStatus
from colossus.apps.lists.tasks import import_subscribers
from colossus.apps.subscribers.constants import ActivityTypes, Status
from colossus.apps.subscribers.fields import MultipleEmailField
from colossus.apps.subscribers.models import Domain, Subscriber
from colossus.apps.accounts.models import User

from colossus.apps.lists.models import MailingList, SubscriberImport

#create logs dir
logs_directory = 'logs'
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)

# Configure logging
logger = logging.getLogger("__name__")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s - %(message)s")
file_handler = logging.FileHandler(os.path.join("logs","remove_unsubs.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_subscribers(email):
    try:
        subscribers = Subscriber.objects.filter(email=email)
        return subscribers
    except Subscriber.DoesNotExist:
        logger.error(f"Subscribers not found")
        return False

    


def get_all_unsubscribed():
    try:
        unsubscribers = Subscriber.objects.filter(status=3,mailing_list__isnull=False)
        return unsubscribers
    except User.DoesNotExist:
        logger.warning(f'Unsubscribers list is empty')
        return False


def remove_unsubscribed():
    unsubscribers = get_all_unsubscribed()
    test_mails = [
        "coboaccess@gmail.com",
        "georgeyoumansjr@gmail.com",
        "coboaccess3@gmail.com",
        "codeinspire1@gmail.com"
    ]
    for unsubscribed in unsubscribers:
        if unsubscribed.email not in test_mails:
            # add_unsubscribers(unsubscribed.email)
            ml_id = unsubscribed.mailing_list
            still_subscribed = get_subscribers(unsubscribed.email)
            email = unsubscribed.email
            logger.info(f"Processing for {email} from unsubscriber list")
            if still_subscribed:
                for subscribed in still_subscribed:
                    try:
                        subs_ml = subscribed.mailing_list
                        subscribed.status = Status.UNSUBSCRIBED
                        subscribed.save()
                        subscribed.mailing_list = None
                        subscribed.save()
                        logger.info(f"Removed {email} from mailing list {str(subs_ml)}")
                    except Exception as e:
                        logger.exception(e)
                        subscribed.delete()
                        logger.warning(f"Deleted {email} due to exception")
                    
            try:
                unsubscribed.mailing_list = None
                unsubscribed.save()
                logger.info(f"unsubscribed email {email} removed from mailing list {str(ml_id)}")
            except Exception as e:
                logger.exception(e)
                unsubscribed.delete()
                logger.warning(f"Deleted Subscribed {email} due to exception")


if __name__ == "__main__":
    remove_unsubscribed()
