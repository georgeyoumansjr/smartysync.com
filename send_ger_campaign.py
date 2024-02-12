import os 
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime

# Define imports and config dictionary
import uuid
import json
import datetime
import requests
from dotenv import load_dotenv 
from django.conf import settings

import pytz

from smtplib import SMTPAuthenticationError
from typing import Dict, List

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail.backends.smtp import EmailBackend
from django.db import transaction
from django.db.models import Q
from django.forms import BoundField
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.lists.constants import ImportFields, ImportStatus
from colossus.apps.lists.tasks import import_subscribers
from colossus.apps.subscribers.constants import ActivityTypes, Status
from colossus.apps.subscribers.fields import MultipleEmailField
from colossus.apps.subscribers.models import Domain, Subscriber, Tag
from colossus.apps.accounts.models import User

from colossus.apps.lists.models import MailingList, SubscriberImport

from colossus.apps.campaigns.models import Campaign
from colossus.apps.campaigns.constants import CampaignStatus


import imaplib
import email
from email.header import decode_header
import os

username = 'contact@gerwholesalers.com'
username = 'mail@thetitandev.com'
username = 'coboaccess@gmail.com'
password = 'Ohappy2023'
password = 'fyrljfsrqmhqkzmd'

imap_server = 'az1-ts111.a2hosting.com'
imap_server = 'mail.thetitandev.com'
imap_server = 'smtp.gmail.com'

imap = imaplib.IMAP4_SSL(imap_server)

imap.login(username, password)

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def get_emails_from_email(batch_name):
    emails = []

    # print(imap.list())

    today = datetime.datetime.today()

    status, messages = imap.select("INBOX")
    N = 30
    messages = int(messages[0])

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        try:
            res, msg = imap.fetch(str(i), "(RFC822)")
        except:
            print('Email fetch error')
            continue
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                # if the email message is multipart

                # if not from the account ve want
                # or not the subject we need, pass
                if subject != 'email-read-test' and subject != f'List of lead emails recieved Yesterday on {batch_name}!':
                    continue


                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print(body)
                            body = body.replace('\r','').replace('\n', '')
                            body = eval(body) # json.loads(body)
                            try:
                                received_at = datetime.datetime.strptime(body['data']['date'], '%Y-%m-%d %H:%M:%S.%f')
                            except:
                                received_at = datetime.datetime.strptime(body['data']['date'], '%Y-%m-%d')

                            if received_at.date() + datetime.timedelta(days=1) != today.date():
                                print('This is an old email.')
                                return []
                            
                            emails = body['data']['emails']
                            return emails

                        """
                        if "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                        """
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        print(body)
                        body = body.replace('\r','').replace('\n', '')
                        body = eval(body) # json.loads(body)
                        try:
                            received_at = datetime.datetime.strptime(body['data']['date'], '%Y-%m-%d %H:%M:%S.%f')
                        except:
                            received_at = datetime.datetime.strptime(body['data']['date'], '%Y-%m-%d')

                        if received_at.date() + datetime.timedelta(days=1) != today.date():
                            print('This is an old email.')
                            return []
                        
                        emails = body['data']['emails']
                        return emails
                if content_type == "text/html":
                    """  
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)
                    # open in the default browser
                    webbrowser.open(filepath)
                    """
                    pass  # don't deal with html emails for now
                print("="*100)
                return []
            
    print(f'No {batch_name} email found in the last {N} emails.')
    
    return emails

def send_campaign_from_email(username, batch_name, pdf_name=None):

    try:
        user = User.objects.get(username=username)

    except User.DoesNotExist:
        print(f'User does not exist, create the user with username : {username}')
        return False
    
    try:
        campaign_name = f'{batch_name}-BATCH-AUTO'
        campaign = Campaign.objects.get(created_by=user, name=campaign_name)

    except Campaign.DoesNotExist:
        print('No campaign. Set the campaign first')
        return False

    try:
        source_mailing_list_name = 'GER BATCH 9'
        source_mailing_list = MailingList.objects.only('pk').get(created_by=user, name=source_mailing_list_name)

    except MailingList.DoesNotExist:
        print(f'No mailing list to get the emails from. Create the mailing list with the name : {source_mailing_list_name}')
        return False

    """
    try:
        mailing_list_name = f'{batch_name}-BATCH-AUTO-CURRENT'
        mailing_list = MailingList.objects.only('pk').get(created_by=user, name=mailing_list_name)

    except MailingList.DoesNotExist:
        print('No mailing list. Setting the mailing list first')
        mailing_list = MailingList.objects.create(
            created_by=user, 
            name = mailing_list_name,
            slug = mailing_list_name.lower(),
            contact_email_address = 'contact@gerwholesalers.com',
            website_url = 'https://thetitandev.com',
            campaign_default_from_name = 'Ger Wholesale',
            campaign_default_from_email = 'contact@gerwholesalers.com',
            campaign_default_email_subject = 'Ger Wholesale',
        )
    """


    
    # if mailing list exists, move to the next one and create the latest batch
    try:
        i = 1
        while True:
            batch_mailing_list_name = f'{batch_name}-BATCH-AUTO-{i}'
            batch_mailing_list = MailingList.objects.get(created_by=user, name=batch_mailing_list_name)

            i += 1
            continue

            # if mailing list exists and has less than 500 subscribers, use that mailing list
            if batch_mailing_list.subscribers_count + len(emails) < 60:
                break

            # if it has more than 500 subscribers, go to the next batch number (and create the mailing list)

    except MailingList.DoesNotExist:
        batch_mailing_list = MailingList.objects.create(
            created_by=user, 
            name = batch_mailing_list_name,
            slug = batch_mailing_list_name.lower(),
            contact_email_address = 'coboaccess@gmail.com',
            website_url = 'https://thetitandev.com',
            campaign_default_from_name = 'Ger Wholesale',
            campaign_default_from_email = 'contact@gerwholesalers.com',
            campaign_default_email_subject = 'Ger Wholesale',
        )

    """
    print(f'Emails are being moved to {batch_mailing_list_name}')
    for subscriber in mailing_list.subscribers.all():
        try:
            subscriber.mailing_list = batch_mailing_list
            subscriber.save()
        except:
            if subscriber.email != 'georgeyoumansjr@gmail.com' or subscriber.email != 'coboaccess@gmail.com':
                subscriber.delete()

    batch_mailing_list.update_subscribers_count()
    print('Emails are moved')
    """

    
    emails = []

     # test the adding next batch if current one has more than 500 emails
    # for i in range(400):  
    #     emails.append(f'{uuid.uuid4()}@gmail.com')

    max_number_of_emails = 60
    counter = 0

    for subscriber in source_mailing_list.subscribers.all():
        if Subscriber.objects.filter(mailing_list__name__startswith=f'{batch_name}-BATCH',
                                     email=subscriber.email).exists():
            continue
        emails.append(subscriber.email)
        counter += 1

        print(f"Email {counter}: {subscriber.email}")

        if counter == max_number_of_emails:
            print(f"Max number of emails is {max_number_of_emails}.")
            break

    print(f'Collected {counter} emails.')

    
    if 'georgeyoumansjr@gmail.com' not in emails:
        emails.append('georgeyoumansjr@gmail.com')

    if 'coboaccess@gmail.com' not in emails:
        emails.append('coboaccess@gmail.com')

    cached_domains = dict()
    status = 2  # SUBSCRIBED

    with transaction.atomic():
        for email in emails:
            email_name, domain_part = email.rsplit('@', 1)
            domain_name = '@' + domain_part

            try:
                domain = cached_domains[domain_name]
            except KeyError:
                domain, created = Domain.objects.get_or_create(name=domain_name)
                cached_domains[domain_name] = domain

            print(email)
            
            subscriber, created = Subscriber.objects.get_or_create(
                email__iexact=email,
                mailing_list=batch_mailing_list,
                defaults={
                    'email': email,
                    'domain': domain
                }
            )

            # georgeyoumansjr and coboaccess sent activity for this campaign should be removed
            # or else it won't send the email to them
            activity = subscriber.activities.filter(activity_type=ActivityTypes.SENT, email=campaign.email)
            if activity.exists():
                activity.delete()


            if created:
                subscriber.create_activity(ActivityTypes.IMPORTED)
            subscriber.status = status
            subscriber.update_date = timezone.now()
            subscriber.save()
        batch_mailing_list.update_subscribers_count()

    campaign.mailing_list = batch_mailing_list
    campaign.status = CampaignStatus.QUEUED  # it might be in SENT state in which case campaign won't be send again
    campaign.save()


    if pdf_name:  # send with attachment
        print('PDF name is :' + pdf_name)
        pdf_path = settings.STATIC_ROOT + '/PDFs/' + pdf_name
        # campaign.send(pdf_name=pdf_name, pdf_path=pdf_path)

    else:  
        pass
        # campaign.send()


    return True






if __name__ == '__main__':

    username = 'ger'
    batch_name = username.upper()
    status = send_campaign_from_email(username, batch_name)

    if status:
        print('Successfuly sent the campaign')
    else:
        print('Fix the errors and try again')

        