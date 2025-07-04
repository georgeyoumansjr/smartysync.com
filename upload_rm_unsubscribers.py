from sheets_api import read_spreadsheet, add_email, check_duplicate_email, get_all_emails


import os 
import django
import logging
import imaplib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime
import imaplib
import email
from email.header import decode_header

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


def get_unsubscribers_from_email():
    
    username = 'coboaccess@gmail.com'
    password = 'fyrljfsrqmhqkzmd'

    imap_server = 'smtp.gmail.com'

    imap = imaplib.IMAP4_SSL(imap_server)

    imap.login(username, password)

    emails = []

    # print(imap.list())

    today = datetime.today()

    status, messages = imap.select("INBOX")
    N = 50
    messages = int(messages[0])

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        try:
            res, msg = imap.fetch(str(i), "(RFC822)")
        except:
            print('Email fetch error')
            logger.warning("Email Fetch Error")
            continue
        
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    encoding = encoding if encoding is not None else 'utf-8'
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    encoding = encoding if encoding is not None else 'utf-8'
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                logger.info("Subject: "+str(subject))
                logger.info("From: "+str(From))
                # if the email message is multipart

                # if not from the account ve want
                # or not the subject we need, pass
                if subject != 'email-read-test' and not subject.endswith("Unsubscribed"):
                    continue
                
                emailValue = str(subject).replace("Unsubscribed","").strip()
                emails.append(emailValue)
            
    print(f'No Unsubscribed email found in the last {N} emails.')
    logger.info(f'No Unsubscribed emails found in the last {N} emails.')
    
    return emails




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
    
    email_unsubscribers = get_unsubscribers_from_email()
    emailUniq, sheetsUniq = get_differences(email_unsubscribers,sheets_unsubs)
    print("Email unique: ")
    print(emailUniq)
    for un_subscriber in emailUniq:
        if un_subscriber in test_mails:
            continue

        add_email(un_subscriber, worksheet)
        
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

