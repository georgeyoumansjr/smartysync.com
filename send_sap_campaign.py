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

from django.db import transaction
from django.db.models import Q
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

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def send_campaign_from_email(username, batch_name, source_mailing_list_name, pdf_name=None, max_number_of_emails=60):

    try:
        user = User.objects.get(username=username)

    except User.DoesNotExist:
        print(f'User does not exist, create the user with username : {username}')
        return False
    
    try:
        campaign_name = f'{batch_name}-BATCH-AUTO Nurture 1'
        campaign = Campaign.objects.get(created_by=user, name=campaign_name)

    except Campaign.DoesNotExist:
        print('No campaign. Set the campaign first')
        return False

    try:
        source_mailing_list = MailingList.objects.only('pk').get(created_by=user, name=source_mailing_list_name)

    except MailingList.DoesNotExist:
        print(f'No mailing list to get the emails from. Create the mailing list with the name : {source_mailing_list_name}')
        return False


    emails = []

     # test the adding next batch if current one has more than 500 emails
    # for i in range(400):  
    #     emails.append(f'{uuid.uuid4()}@gmail.com')

    counter = 0

    for subscriber in source_mailing_list.subscribers.all():
        if Subscriber.objects.filter(mailing_list__name__startswith=f'{source_mailing_list_name} AUTO',
                                     email=subscriber.email).exists():
            continue
        emails.append(subscriber.email)
        counter += 1

        print(f"Email {counter}: {subscriber.email}")

        if counter == max_number_of_emails:
            print(f"Max number of emails is {max_number_of_emails}.")
            break

    print(f'Collected {counter} emails.')

    if counter == 0:
        print('No emails to send. Either script is done with the current set of emails or there is a problem with the logic.')
        print(f'Source mailing list name : {source_mailing_list_name}')
        print(f'Source mailing list subscriber count : {source_mailing_list.subscribers_count}')
        
        if source_mailing_list.subscribers_count == 0:
            print('Source mailing list is empty. Please make sure it\'s the right mailing list.')

        prefix = f'{source_mailing_list_name} AUTO'
        existing_mailing_lists_with_prefix = MailingList.objects.filter(name__startswith=prefix)
        print(f"Existing mailing lists with prefix {prefix} : ")

        if not existing_mailing_lists_with_prefix.exists():
            print('None')
        for m in existing_mailing_lists_with_prefix:
            print(f'Name : {m.name}')
            print(f'Subscriber Count : {m.subscribers_count}')

        return False

    try:
        i = 1
        while True:
            batch_mailing_list_name = f'{source_mailing_list_name} AUTO PT-{i}'
            batch_mailing_list = MailingList.objects.get(created_by=user, name=batch_mailing_list_name)

            i += 1
            continue

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
    

    
    if 'georgeyoumansjr@gmail.com' not in emails:
        emails.append('georgeyoumansjr@gmail.com')

    if 'coboaccess@gmail.com' not in emails:
        emails.append('coboaccess@gmail.com')

    if 'coboaccess3@gmail.com' not in emails:
        emails.append('coboaccess3@gmail.com')

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
        campaign.send(pdf_name=pdf_name, pdf_path=pdf_path)

    else:  
        campaign.send()


    return True






if __name__ == '__main__':

    username = 'sap'
    batch_name = username.upper()
    source_mailing_list_name = 'SAP BATCH 3'
    max_number_of_emails = 50
    pdf_name = 'Introduction to React.pdf'

    status = send_campaign_from_email(username, batch_name, source_mailing_list_name,
                                    pdf_name=pdf_name, max_number_of_emails=max_number_of_emails)

    if status:
        print('Successfuly sent the campaign')
    else:
        print('Fix the errors and try again')

        