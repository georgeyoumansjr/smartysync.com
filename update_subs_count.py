import os 
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime


from dotenv import load_dotenv 
from django.conf import settings

from typing import Dict, List

from colossus.apps.lists.models import MailingList


def update_counts():
    mailing_lists = MailingList.objects.all()

    # Iterate over each MailingList object and call update_subscribers_count() method
    for mailing_list in mailing_lists:
        print("update count for "+str(mailing_list.name))
        mailing_list.update_subscribers_count()
        mailing_list.save()

if __name__=="__main__":
    update_counts()