import imaplib
import email
import os
import re
import pytz

from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv 
from django.conf import settings


pathdot = os.path.join(settings.BASE_DIR,".env")
load_dotenv(pathdot)

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


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)


def get_non_existing_emails_and_return_list():
    username = 'contact@gerwholesalers.com'
    username = 'coboaccess@gmail.com'
    username = 'georgeyoumansjr@gmail.com'

    password = 'Ohappy2023'
    password = 'fyrljfsrqmhqkzmd'  # coboaccess
    password = 'lhhd pvex quyg pkxx'  # georgeyoumansjr

    imap_server = 'mail.thetitandev.com'
    imap_server = 'smtp.gmail.com'



    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, password)

    emails = []

    pattern = r'<(.*?)>'
    pattern = r'"mailto:(.*?)"'
    pattern = r"<[-A-Za-z0-9!#$%&'*+/=?^_`{|}~]+(?:\.[-A-Za-z0-9!#$%&'*+/=?^_`{|}~]+)*@(?:[A-Za-z0-9](?:[-A-Za-z0-9]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[-A-Za-z0-9]*[A-Za-z0-9])?>"

    mailbox = "[Gmail]/Spam"

    status, messages = imap.select(mailbox)
    N = 50
    messages = int(messages[0])

    print('Removing non-existing emails.')

    for i in range(messages, messages-N, -1):
        # fetch the email message by ID
        try:
            res, msg = imap.fetch(str(i), "(RFC822)")
        except:
            print('Email fetch error')
            continue
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
      
                if subject != 'Undelivered Mail Returned to Sender' and subject != 'Mail delivery failed: returning message to sender':
                    continue

                if msg.is_multipart():
                    for part in msg.walk():
                        try:
                            body = part.get_payload(decode=True).decode()
                            break
                        except:
                            pass
                else:
                    body = msg.get_payload(decode=True).decode()

                try:
                    email_address = re.findall(pattern, body)[0]
                except:
                    continue

                
                print(f'Found : {email_address}')
                emails.append(email_address)
            
    print(f'non-existing emails : {emails}')
    return emails












