import requests
import os 
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime

# Define imports and config dictionary
import time
import json
import logging
from dotenv import load_dotenv 
from django.conf import settings


from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.subscribers.models import Domain, Subscriber

logging.basicConfig(filename='email_checker.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_email(to_email:str):
    time.sleep(15)
    url = 'http://191.101.233.115:8080/v0/check_email'
    headers = {
        'Content-Type': 'application/json',
        # 'authorization':'8191f124-e07e-11ee-b82e-2b0c0b217aa7'
        }
    data = {
        "to_email": to_email
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        print("Error:", response.status_code)
        print(response)
        return None

def append_to_file(file_path, data):
    with open(file_path, "a") as f:
        json_string = json.dumps(data)
        f.write(json_string + "\n")

def filter_get_invalid_email():

    subs_obj = Subscriber.objects.values_list('email',flat=True).distinct()
    invalid_emails = []
    unknown_emails = []
    valid_emails = []
    other_emails = []

    for sub in subs_obj:
        check_resp = check_email(sub)
        logging.info("Email: %s, Check Result: %s", sub, check_resp)

        append_to_file("all_list.json",check_resp)

        if check_resp:
            if check_resp["is_reachable"] == "invalid":
                invalid_emails.append(sub)
                append_to_file("invalid_emails.json", check_resp)

            elif check_resp['is_reachable'] == "unknown":
                unknown_emails.append(sub)
                append_to_file("unknown_emails.json", check_resp)

            elif check_resp['is_reachable'] == "safe":
                valid_emails.append(sub)
                append_to_file("safe_emails.json", check_resp)

            else:
                other_emails.append(sub)
                append_to_file("other_emails.json", check_resp)
    
    print("Invalid Emails:", invalid_emails)
    print("Unknown Emails:", unknown_emails)
    print("Valid Emails:", valid_emails)
    print("Other Emails:", other_emails)



if __name__ == "__main__":
    filter_get_invalid_email()
