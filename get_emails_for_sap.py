from facebook_scripts_utils import send_campaign_from_email

def main():
    username = 'sap'
    batch_name = username.upper()
    pdf_name = 'Introduction to React.pdf'
    status = send_campaign_from_email(username, batch_name, pdf_name)

    if status:
        print('Successfuly sent the campaign')
    else:
        print('Fix the errors and try again')
    
    return status

        
if __name__ == '__main__':
    main()