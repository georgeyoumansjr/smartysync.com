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






invalid_email_list = ['0798542218@gmail.com',
 'Abubakaraisha1775@gmail.com',
 'BanguhaHussein@gmail.com',
 'Benitngood7@gmail.com',
 'ChriOwus@gmail.com',
 'Costybrown12@gmail.com',
 'DANNYPAin@gmail.com',
 'Davidkeme989@gmail.com',
 'Dukorerimananenjamin2@gmail.com',
 'Elchdaiiratuzi@gmail.com',
 'Ericmdn58@gmail.com',
 'Gmugisha386@gmail.com',
 'Jiradukundj@gmail.com',
 'Johnjohnclirse900@gmail.com',
 'K05587188@gmail.com',
 'Kanyaramonicah36@gmail.com',
 'Kayinamuradominic77@gmail.com',
 'Marietash750@gmail.com',
 'Maxwedatsa12@gmail.com',
 'Michaeltsnoe02@gmail.com',
 'Niyigenafrancine233@gmail.com',
 'Onexphore@gmail.com',
 'Shadrackomari170@gmail.com',
 'Sibomajimmy57@gmail.com',
 'Tuyizereeugenie02@gmail.com',
 'Warwathepeninahkariu@gmail.com',
 'Westg975@gmail.com',
 'Wilrescue21@gmail.com',
 'Wjeminah12@gmail.com',
 'abdulkarimumugiraneza@gmail.com',
 'abeldogah69@gmail.com',
 'adamtamimusuna@gmail.com',
 'adubrigth1988@gmail.com',
 'aimedukuzumuremyi33@gmail.com',
 'akoaafua@gmail.com',
 'alhassansoalejohn@gmail.com',
 'andohpatrick12r@gmail.com',
 'archampogsylvestet@gmail.com',
 'ayilinyathomas70@gmail.com',
 'bazirakecelestin924@gmail.com',
 'chatrillionaire576@gmail.com',
 'cutisagbe123@gmail.com',
 'dekakwesitikesie@gmail.com',
 'divinekumahor0@gmail.com',
 'douglasboampong716@gmail.com',
 'dusengeleo44@gmail.com',
 'elizabeth.kariuki1954@gmail.com',
 'eogori00@gmail.com',
 'ericadombila7@gmail.com',
 'euniternyarondiek@gmail.com',
 'felixbenson911@gmail.com',
 'florayankey20@gmail.com',
 'gumisiriza268@gmail.com',
 'irenesymo482@gmail.com',
 'jerriesvectorg123@gmail.com',
 'jmunanie07@gmail.com',
 'josephnshimiyinana633@gmail.com',
 'juliusseklou1@gmail.com',
 'kamanasamuel65@gmail.com',
 'kwabenanyame859@gmail.com',
 'kwizaradan736@gmail.com',
 'maggypellin90@gmail.com',
 'merciemurgaz65@gmail.com',
 'mukamiruth112@gmail.com',
 'munyalimandewilson@gmail.com',
 'munyanezarobben7@gmail.com',
 'musahakinuasalaba@gmail.com',
 'mustaphawumbei3@gmail.com',
 'musuhqbud@gmail.com',
 'mwongelngumbi20@gmail.com',
 'nazairenshuti@gmail.com',
 'ndayisengaaugustin95@gmail.com',
 'ndayizeyelabani240@gmail.com',
 'ndikumaibrahik1985@gmail.com',
 'ngendahimanasamuel03@gmail.com',
 'nishimwaangeloice@gmail.com',
 'niyomwungerjd23@gmail.com',
 'nonidesigner.marymuthoni38142664@gmail.com',
 'nyabyendaeric402@gmail.com',
 'nzayikoreragermain525@gmail.com',
 'otoobright44@gmail.com',
 'ousmatoure9175@gmail.com',
 'ppollinaire25@gmail.com',
 'priscdakwa12345@gmail.com',
 'puritywa20@gmail.com',
 'shembus06@gmail.com',
 'turikumwenimnajiscal@gmail.com',
 'uwatheo78@gmail.com',
 'yevuagbisamiel@gmail.com']

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

