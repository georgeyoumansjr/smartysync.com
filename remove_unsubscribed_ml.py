import os 
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime


from dotenv import load_dotenv 
from django.conf import settings

from typing import Dict, List

from django.utils.translation import gettext, gettext_lazy as _
from colossus.apps.subscribers.models import Domain, Subscriber, Unsubscribers


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
        unsubscribers = Subscriber.objects.filter(status=3)
        return unsubscribers
    except Subscriber.DoesNotExist:
        logger.warning(f'Unsubscribers list is empty')
        return False
    
def get_still_subscribed(unsubscribed_email):
    try:
        still_subscribed = Subscriber.objects.filter(email=unsubscribed_email, status=2, mailing_list__isnull=False)
        return still_subscribed
    except Subscriber.DoesNotExist:
        print("No Still Subscribed emails found")
        return False


def remove_unsubscribed():
    unsubscribers = get_all_unsubscribed()
    test_mails = [
        "coboaccess@gmail.com",
        "georgeyoumansjr@gmail.com",
        "coboaccess3@gmail.com",
    ]
    for unsubscribed in unsubscribers:
        if unsubscribed.email not in test_mails:
            # add_unsubscribers(unsubscribed.email)
            ml_id = unsubscribed.mailing_list
            still_subscribed = get_subscribers(unsubscribed.email)
            email = unsubscribed.email
            logger.info(f"Processing for {email} from unsubscriber list")
            try:
                unsubscribe = Unsubscribers(email=email)
                unsubscribe.save()
                logger.info(f"{email} added in unsubscriber")
            except Exception as e:
                print(e)
            if still_subscribed:
                for subscribed in still_subscribed:
                    try:
                        subs_ml = subscribed.mailing_list
        
                        subscribed.delete()
                        logger.info(f"Removed {email} from mailing list {str(subs_ml)}")
                    except Exception as e:
                        logger.exception(e)
                        logger.warning(f"Unable to Delete {email} due to exception")
            try:
                unsubscribed.delete()
                logger.info(f"Deleted email {email} removed from mailing list {str(ml_id)}")
            except Exception as e:
                logger.exception(e)
                logger.warning(f"Unable to Delete Subscribed {email} due to above exception")


if __name__ == "__main__":
    remove_unsubscribed()
