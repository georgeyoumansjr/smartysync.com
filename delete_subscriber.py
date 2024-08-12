import os 
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime
from typing import List, Union

# Define imports and config dictionary
import sys
from dotenv import load_dotenv 
from django.conf import settings
from django.db.models import QuerySet

from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.accounts.models import User

from colossus.apps.subscribers.models import Subscriber

def get_subscriber(email:str)-> list:
    return Subscriber.objects.filter(email=email)



def delete_subscriber(email: Union[str, None])-> bool:

    objects = Subscriber.objects.filter(email= email)
    if objects:
        for subscriber in objects:
            try:
                subs_ml = subscriber.mailing_list
                print(f"Deleting subscriber with email {email} in mailing list {str(subs_ml)}")
                subscriber.delete()
                subs_ml.update_subscribers_count()
                subs_ml.save()
            except Exception as e:
                print(f"Unable to delete Subscriber with emai {email}")
        return True
    return False

def delete_subscribers(subscriberList: list)-> bool:
    if subscriberList:
        for subscriber in subscriberList:
            try:
                subs_ml = subscriber.mailing_list
                print(f"Deleting subscriber with email {email} in mailing list {str(subs_ml)}")
                subscriber.delete()
                subs_ml.update_subscribers_count()
                subs_ml.save()
            except Exception as e:
                print(f"Unable to delete Subscriber with emai {email}")
        return True
    
    return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python delete_subscriber.py "<email>"')
    else:
        email = sys.argv[1]
        subscribers = get_subscriber(email)
        if subscribers:
            u_input = input(f"Are You sure you want to delete all {len(subscribers)} Subscriber with email {email} (Y/N)?: ")
            if u_input.lower() == "y":
                delete_subscribers(subscribers)
            else:
                print("Try again")

