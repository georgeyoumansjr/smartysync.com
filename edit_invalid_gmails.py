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


invalid_gmail_domains = [
    '@g.mail.com',
 '@gmaol.com',
 '@gmal.com',
 '@gmail.co',
 '@gmaii.com',
 '@gmail.com.com',
 '@gnail.com',
 '@gmail.come',
 '@gmial.com',
 '@gmil.com',
 '@gmail.con',
 '@gma.com',
 '@gmail.cim',
 '@g.mail',
 '@gmail.cgmail',
 '@gemail.com',
 '@gmail.comm',
 '@gml.com',
 '@g-mail.com',
 '@gmeil.com',
 '@gmavsil.com',
 '@gmail.col',
 '@gamail.com',
 '@gmail.cm',
 '@gmail.comz',
 '@gimail.com',
 '@gmai.com',
 '@gmail.com725248074',
 '@gmeal.com',
 '@gmail.c',
 '@gmail.hasscom',
 '@gmael.com',
 '@gemeil.com',
 '@gmail.coml',
 '@gmail.com0791582919'
 '@mailg.com'
]


def update_domain(subs_obj,invalid_domain):
    try:
        emailValue = subs_obj.email
        print("Updating the email value for email: ", emailValue)
        subs_obj.email = emailValue.replace(invalid_domain,"@gmail.com")
        subs_obj.save()
    except Exception as e:
        print(e)


for domain in invalid_gmail_domains:
    obj_with_domain = Subscriber.objects.filter(email__endswith=domain)
    print("Processing for domain: ",domain)
    for subscriber_obj in obj_with_domain:
        update_domain(subscriber_obj,domain)



