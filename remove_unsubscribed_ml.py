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
from colossus.apps.subscribers.models import Domain, Subscriber, Unsubscribers
from colossus.apps.accounts.models import User

from colossus.apps.lists.models import MailingList, SubscriberImport

from colossus.apps.campaigns.models import Campaign
from colossus.apps.campaigns.constants import CampaignStatus

from email.header import decode_header
import os


def get_subscribers(email):
    try:
        subscribers = Subscriber.objects.filter(email=email,status=2)
        return subscribers
    except Subscriber.DoesNotExist:
        print(f"Subscribers not found")
        return False


def get_mailing_lists(userid):
    try:
        mailing_list = MailingList.objects.get(created_by_id=userid)
        return mailing_list
    except MailingList.DoesNotExist:
        print(f'User does not exist, create the user with userid : {userid}')
        return False
    

def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        print(f'User does not exist, create the user with username : {username}')
        return False


def get_users():
    try:
        users = User.objects.all().values('id', 'username', 'email')
        return users
    except User.DoesNotExist:
        print(f'empty')
        return False
    

def get_all_unsubscribed():
    try:
        unsubscribers = Subscriber.objects.filter(status=3)
        return unsubscribers
    except User.DoesNotExist:
        print(f'empty')
        return False
    
def get_unsubscribers():
    try:
        unsubscribers = Unsubscribers.objects.all()
        # Extract email addresses from Unsubscriber objects
        email_addresses = [unsubscriber.email for unsubscriber in unsubscribers]
        return email_addresses
    except Unsubscribers.DoesNotExist:
        print(f"Unsubscribers list empty")
        return False


def remove_unsubscribed():
    unsubscribers = get_all_unsubscribed()
    test_mails = [
        "coboaccess@gmail.com",
        "georgeyoumansjr@gmail.com",
        "coboaccess3@gmail.com",
        "codeinspire1@gmail.com"
    ]
    existing_unsubscribers = get_unsubscribers()
    for unsubscribed in unsubscribers:
        if unsubscribed.email not in test_mails and unsubscribed.email not in existing_unsubscribers:
            still_subscribers = get_subscribers(unsubscribed.email)
            if still_subscribers:
                for subscriber in still_subscribers:
                    add_unsubscribers(subscriber.email)
                    subscriber.delete()
            else:
                add_unsubscribers(unsubscribed.email)
                unsubscribed.delete()


def add_unsubscribers(email):
    try:
        unsubscriber, created = Unsubscribers.objects.get_or_create(email = email)

        if unsubscriber:
            print(f"Duplicate: The email {email} already exists in the Unsubscribers list")
        if created:
            print(f"Created: The email {email} is added to Unsubscribers list")

    except Exception as e:
        print(f"An error occurred: {str(e)} while adding unsubscribers")

if __name__ == "__main__":
    remove_unsubscribed()
