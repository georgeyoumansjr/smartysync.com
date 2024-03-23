import os 
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "colossus.settings")
django.setup()

from datetime import datetime

# Define imports and config dictionary

from dotenv import load_dotenv 
from django.conf import settings

from django.utils.translation import gettext, gettext_lazy as _

from colossus.apps.accounts.models import User

from colossus.apps.lists.models import MailingList




def get_delete_mailing_list(username, source_mailing_list_name=None):
    try:
        user = User.objects.get(username=username)

    except User.DoesNotExist:
        print(f'User does not exist, create the user with username : {username}')
        return False
    
    if source_mailing_list_name:
        try:
            source_mailing_list = MailingList.objects.only('pk').get(created_by=user, name=source_mailing_list_name)

        except MailingList.DoesNotExist:
            print(f'No mailing list to get the emails from. Create the mailing list with the name : {source_mailing_list_name}')
            return False
        
    else:
        source_mailing_list = MailingList.objects.only('pk').filter(created_by=user)

        if not source_mailing_list:
            print(f'No mailing list to get the emails from. the user :{username}')
            return False
        
    if source_mailing_list_name:

        print(f'Source mailing list name : {source_mailing_list_name}')
        print(f'Source mailing list subscriber count : {source_mailing_list.subscribers_count}')
            
        if source_mailing_list.subscribers_count == 0:
            print('Source mailing list is empty. Please make sure it\'s the right mailing list.')

        prefix = f'{source_mailing_list_name} AUTO'
        existing_mailing_lists_with_prefix = MailingList.objects.filter(name__startswith=prefix)
        
        if existing_mailing_lists_with_prefix:
            print(f"Existing mailing lists with prefix {prefix} : ")
            for mailing_list in existing_mailing_lists_with_prefix:
                mailing_list.delete()
                print("Deleted sub Mailing list "+str(mailing_list))

    else:
        auto_pt_mailing_lists = MailingList.objects.filter(name__contains='AUTO PT-',created_by=user)

        if auto_pt_mailing_lists:
            # Delete each mailing list
            for mailing_list in auto_pt_mailing_lists:
                
                mailing_list.delete()
                print("Deleted sub Mailing List "+ str(mailing_list))


    return True



if __name__ == '__main__':

    username = 'sap'
    batch_name = username.upper()

    if len(sys.argv) != 2:
        print('Usage: python clear_automate_ml.py "<main_list_name>"')
    else:
        
        source_mailing_list_name = sys.argv[1]
        
        if source_mailing_list_name:

            status = get_delete_mailing_list(username, source_mailing_list_name)

            if status:
                print('Successfuly deleted the ML')
            else:
                print('Fix the errors and try again')
        
        else:
            u_input = input("Are You sure you want to delete all Script Generate Mailing Lists (Y/N)?: ")
            if u_input.upper() == "Y":
                status = get_delete_mailing_list(username, source_mailing_list_name)

                if status:
                    print('Successfuly deleted the ML')
                else:
                    print('Fix the errors and try again')

            else:
                print("Exited the Script")
        