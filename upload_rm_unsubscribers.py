from sheets_api import read_spreadsheet, add_email, check_duplicate_email, get_all_emails


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



spreadsheet_id = "1-Ic6tHRwEZ2CwD2UYq2gm2NNPfT6NHavHBDibgNFiqo"

# Read the spreadsheet
spreadsheet = read_spreadsheet(spreadsheet_id)


#create logs dir
logs_directory = 'logs'
if not os.path.exists(logs_directory):
    os.makedirs(logs_directory)

# Configure logging
logger = logging.getLogger("__name__")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(name)s - %(message)s")
file_handler = logging.FileHandler(os.path.join("logs","upload_remove_unsubs.log"))
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
        unsubscribers = Unsubscribers.objects.values_list('email',flat=True)
        unsubscribers = list(unsubscribers)
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


def get_differences(db_list,sheets_list):
    set1 = set(db_list)
    set2 = set(sheets_list)

    # Elements in list1 but not in list2
    dbDiff = set1 - set2

    # Elements in list2 but not in list1
    sheetsDiff = set2 - set1

    return list(dbDiff), list(sheetsDiff)



def upload_remove_unsubscribed():
    unsubscribers = get_all_unsubscribed()
    sheets_unsubs = []
    if spreadsheet:
        worksheet = spreadsheet.sheet1
        sheets_unsubs = get_all_emails(worksheet)
    
    test_mails = [
        "coboaccess@gmail.com",
        "georgeyoumansjr@gmail.com",
        "coboaccess3@gmail.com",
    ]

    dbUnique, sheetsUnique = get_differences(unsubscribers,sheets_unsubs)
    print(dbUnique)
    print(sheetsUnique)
    
    for un_subscriber in dbUnique:
        if un_subscriber in test_mails:
            continue

        add_email(un_subscriber, worksheet)

    for un_subscriber in sheetsUnique:
        if un_subscriber in test_mails:
            continue
        still_subscribed = get_subscribers(un_subscriber)
        email = un_subscriber
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
                    subs_ml.update_subscribers_count()
                    subs_ml.save()
                    logger.info(f"Removed {email} from mailing list {str(subs_ml)}")
                except Exception as e:
                    logger.exception(e)
                    logger.warning(f"Unable to Delete {email} due to exception")


if __name__ == "__main__":
    # remove_unsubscribed()
    # print(get_all_unsubscribed())
    upload_remove_unsubscribed()
    # psass

