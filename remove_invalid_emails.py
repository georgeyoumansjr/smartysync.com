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






invalid_email_list = ['1804ryder@gmail.com',
 'Edouardtuyishimire3@gmail.com',
 'Gedeoishimwe52@gmail.com',
 'Ndatimana.fabrice87@gmail.com',
 'NgarambeAlphonse39@gmail.com',
 'Niyifashapeninah73@gmail.com',
 'Niyigeaolivier058@gmail.com',
 'Niyomukiz766@gmail.com',
 'Prinncemoise12002@gmail.com',
 'bigirimanasamue4404@gmail.com',
 'bizumuremynoel047@gmail.com',
 'boazsibomana84@gmail.com',
 'freedomagbavitorfreedomagbavitor3@gmail.com',
 'ishakafrancs@gmail.com',
 'ishima222@gmail.com',
 'jessicagasaro3@gmail.com',
 'mugishaclaude530@gmail.com',
 'muntarikunpong234@gmail.com',
 'peacemutoro@gmail.com',
 'ringshine71@gmail.com',
 'teta24@gmail.com',
 'williamankomah@gmail.com',
 'yvesrukundo04@gmail.com']

spreadsheet_id = "12X0cNw64w0dRhDl3NgyE4Bl99XduspabqJOYxXd_i4E"

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
file_handler = logging.FileHandler(os.path.join("logs","remove_invalid_emails.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_subscribers(email):
    try:
        subscribers = Subscriber.objects.filter(email=email)
        return subscribers
    except Subscriber.DoesNotExist:
        logger.error(f"Subscribers not found")
        return False

def get_still_subscribed(email):
    try:
        still_subscribed = Subscriber.objects.filter(email=email)
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



def upload_remove_invalid():
    
    sheets_unsubs = []
    if spreadsheet:
        worksheet = spreadsheet.sheet1
        sheets_unsubs = get_all_emails(worksheet)
    
    
    for subscriber in invalid_email_list:
        
        if subscriber not in sheets_unsubs:
            add_email(subscriber, worksheet)

        
        still_subscribed = get_subscribers(subscriber)
        email = subscriber
        logger.info(f"Processing for {email} from invalid email list")
        if still_subscribed:
            for subscribed in still_subscribed:
                print(subscribed)
                try:
                    subs_ml = subscribed.mailing_list
    
                    subscribed.delete()
                    subs_ml.update_subscribers_count()
                    subs_ml.save()
                    logger.info(f"Removed {email} from mailing list {str(subs_ml)}")
                except Exception as e:
                    logger.exception(e)
                    logger.warning(f"Unable to Delete {email} due to exception")

    for subscriber in sheets_unsubs:
        if subscriber not in invalid_email_list:
            still_subscribed = get_subscribers(subscriber)
        email = subscriber
        logger.info(f"Processing for {email} from Spreadsheet list")
        if still_subscribed:
            for subscribed in still_subscribed:
                print(subscribed)
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
    upload_remove_invalid()
    # psass

