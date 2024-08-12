import requests
import os 
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime

# Define imports and config dictionary
import uuid
import json
import logging
from dotenv import load_dotenv 
from django.conf import settings


from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.subscribers.models import Domain, Subscriber

logging.basicConfig(filename='email_invalid.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')







invalid_domains = ['@g.mail.com',
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
 '@gmail.com0791582919']


subscriber_list =  list(Subscriber.objects.all().values_list("email",flat=True))
invalid_Demails = {}

for domain in invalid_domains:
    d = domain.replace("@","")
    filtered_emails = my_list = [x for x in subscriber_list if x.endswith(d)]
    invalid_Demails[domain] = filtered_emails

with open("domainInvalidGmails.json","w") as filedD:
    filedD.write(json.dumps(invalid_Demails))
print(invalid_Demails)

