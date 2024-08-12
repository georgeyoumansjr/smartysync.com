import os
import django
import asyncio
import aiohttp
import logging
import json
from dotenv import load_dotenv
from django.conf import settings
from django.utils.translation import gettext, gettext_lazy as _

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from colossus.apps.subscribers.models import Subscriber

logging.basicConfig(filename='email_checker.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def check_email(to_email: str, session: aiohttp.ClientSession):
    url = 'http://191.101.233.115:8080/v0/check_email'
    headers = {'Content-Type': 'application/json'}
    data = {"to_email": to_email}

    async with session.post(url, json=data, headers=headers) as response:
        if response.status == 200:
            result = await response.json()
            return result
        else:
            logging.error("Error for email %s: %s", to_email, response.status)
            return None

async def process_emails(emails):
    invalid_emails = []
    unknown_emails = []
    valid_emails = []
    other_emails = []

    async with aiohttp.ClientSession() as session:
        tasks = [check_email(email, session) for email in emails]
        results = await asyncio.gather(*tasks)

    for email, check_resp in zip(emails, results):
        logging.info("Email: %s, Check Result: %s", email, check_resp)
        if check_resp:
            if check_resp["is_reachable"] == "invalid":
                invalid_emails.append(email)
                append_to_file("invalid_emails.json", check_resp)
            elif check_resp['is_reachable'] == "unknown":
                unknown_emails.append(email)
                append_to_file("unknown_emails.json", check_resp)
            elif check_resp['is_reachable'] == "safe":
                valid_emails.append(email)
                append_to_file("safe_emails.json", check_resp)
            else:
                other_emails.append(email)
                append_to_file("other_emails.json", check_resp)

    print("Invalid Emails:", invalid_emails)
    print("Unknown Emails:", unknown_emails)
    print("Valid Emails:", valid_emails)
    print("Other Emails:", other_emails)

def append_to_file(file_path, data):
    with open(file_path, "a") as f:
        json_string = json.dumps(data)
        f.write(json_string + "\n")

def filter_get_invalid_email():
    subs_obj = Subscriber.objects.values_list('email', flat=True).distinct()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_emails(subs_obj))

if __name__ == "__main__":
    filter_get_invalid_email()
