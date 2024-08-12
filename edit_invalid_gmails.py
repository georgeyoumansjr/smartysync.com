from sheets_api import read_spreadsheet, add_multiple_data, get_existing_data


import os 
import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime


from dotenv import load_dotenv 
from django.conf import settings

from typing import Dict, List
import re

from django.utils.translation import gettext, gettext_lazy as _
from colossus.apps.subscribers.models import Domain, Subscriber, Unsubscribers

spreadsheet_id = "1avrcBD_FdtXZrvXwYe-mLU041EgQcCH9LuuAOShKF-w"

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
file_handler = logging.FileHandler(os.path.join("logs","edit_invalid_gmails.log"))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)



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



def get_filtered_domain():
    domain_list = list(Domain.objects.values_list('name', flat=True).distinct())

    valid_domains = [
        "@gmail.com",
        '@gerties.org',
        '@graciahotels.co.ke',
        '@g020.com',
        '@googlemail.com',
        '@google.com',
        '@gamal.com',
        '@geimer.com',
        "@gimail.rw",
        "@Gmail.com"
    ]

    pattern = re.compile(r"^(@g|@\d+(\.)?g|@mailg).*$", re.IGNORECASE)

    invalid_gmail_domains = [domain for domain in domain_list if pattern.match(domain) and domain not in valid_domains]
    logger.info("Filtered Domains list prepared")
    return invalid_gmail_domains


def update_domain(subs_obj,invalid_domain):
    try:
        emailValue = subs_obj.email
        logger.info(f"Updating the email value for email: {emailValue}")
        numDomainPattern = re.compile(r"^@(\d+)(\.)?g",re.IGNORECASE)
        # print(subs_obj)
        matchedData = numDomainPattern.match(invalid_domain)
        # print(matchedData)

        if matchedData:
            logger.info(f"Domain with numeric value discovered: {invalid_domain}")
            emailValueUpdate = emailValue.split("@")[0] + matchedData[1] +"@gmail.com"
            # print(emailValueUpdate)
            subs_obj.email = emailValueUpdate
            subs_obj.save()
            return [emailValue, emailValueUpdate]
        
        emailValueUpdate = emailValue.replace(invalid_domain,"@gmail.com")
        subs_obj.email = emailValueUpdate
        subs_obj.save()
        return [emailValue, emailValueUpdate]
    except Exception as e:
        logger.warning(f"Exception occured: {e}")
        return False

if __name__=="__main__":

    if spreadsheet:
        worksheet = spreadsheet.sheet1

    

    invalid_gmail_domains = get_filtered_domain()
    
    
    existing_data = get_existing_data(worksheet)

    for domain in invalid_gmail_domains:
        obj_with_domain = Subscriber.objects.filter(email__endswith=domain)
        
        logger.info(f"Processing for domain: {domain}",)
        if obj_with_domain:
            for subscriber_obj in obj_with_domain:
                subs_ml = subscriber_obj.mailing_list
                logger.info(f"Processing for subscriber {subscriber_obj.email} in mailing list {str(subs_ml)}")
                update_data = update_domain(subscriber_obj,domain)
                if update_data:
                    add_multiple_data(update_data, worksheet, [0,1], existing_data)



