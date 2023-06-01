from datetime import datetime

# Define imports and config dictionary
import msal
import requests
from dotenv import load_dotenv 
import os 
from django.conf import settings

import pytz


def convert_date(str_date: str) -> datetime:
    date = datetime.strptime(str_date.strip(), '%Y-%m-%d %H:%M:%S')
    return pytz.utc.localize(date)


def normalize_email(email: str) -> str:
    from colossus.apps.subscribers.models import Subscriber
    return Subscriber.objects.normalize_email(email)


def normalize_text(text: str) -> str:
    if text is None:
        return ''
    text = str(text)
    text = ' '.join(text.split())
    return text




pathdot = os.path.join(settings.BASE_DIR,".env")
load_dotenv(pathdot)
config = {
  'client_id': os.getenv("CLIENT_ID"),
  'client_secret': os.getenv("CLIENT_SECRET"),
  'authority': 'https://login.microsoftonline.com/'+os.getenv("TENANT_ID"),
  'scope': ['https://graph.microsoft.com/.default']
}

# Create an MSAL instance providing the client_id, authority and client_credential parameters
client = msal.ConfidentialClientApplication(config['client_id'], authority=config['authority'], client_credential=config['client_secret'])
# print(client)""
# Make an MS Graph call


def get_non_existing_emails_and_return_list():
    mail_folders = ["junkemail","sentitems","inbox"]
    pagination = True
    emails = []
    for folder in mail_folders:
        url = 'https://graph.microsoft.com/v1.0/users/'+os.getenv("USER_ID")+f"/mailFolders('{folder}')/messages"
        token_result = client.acquire_token_silent(config['scope'], account=None)
        if not token_result:
            token_result = client.acquire_token_for_client(scopes=config['scope'])

        if 'access_token' in token_result:
            headers = {
                'Authorization': 'Bearer ' + token_result['access_token'],
                "Content-Type": "application/json"
                }

            while url:
                try:
                    graph_result = requests.get(url=url, headers=headers).json()
                    for result in graph_result['value']:
                        from_email = result['from']['emailAddress']['address']
                        if 'MAILER-DAEMON@mailchannels.net' == from_email:
                            # print('from : ',from_email)
                            to_email = result['toRecipients'][0]['emailAddress']['address']
                            print('Failed email : ', to_email)
                            emails.append(to_email)

                    #graph_results.extend(graph_result['value'])
                    if (pagination == True):
                        url = graph_result['@odata.nextLink']
                    else:
                        url = None
                except:
                    break
        else:
            print(token_result.get('error'))
            print(token_result.get('error_description'))
            print(token_result.get('correlation'))
            return []

    return emails














