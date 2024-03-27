import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

# Set the credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('google-sheets-auth.json', scope)

# Authorize the client
gc = gspread.authorize(creds)

def read_spreadsheet(sheet_id):
    try:
        spreadsheet = gc.open_by_key(sheet_id)
        return spreadsheet
    except gspread.exceptions.APIError as e:
        print("An error occurred:", e)
        return None

# Function to add email to the spreadsheet
def add_email(email, worksheet):
    # Check if the email already exists to avoid duplicates
    if check_duplicate_email(worksheet, email):
        print("Email already exists in the sheet.")
    else:
        # Append the email to the sheet
        worksheet.append_row([email])
        print("Email added successfully.")

# Function to check for duplicate email
def check_duplicate_email(worksheet, email):
    # Get all values in the first column (assuming email addresses are in the first column)
    email_column = worksheet.col_values(1)

    # Check if email exists
    return email in email_column

def get_all_emails(worksheet):
    # Get all values in the first column (assuming email addresses are in the first column)
    email_column = worksheet.col_values(1)[0:]  # Exclude header row
    return email_column

if __name__ == "__main__":
    # Example spreadsheet ID
    spreadsheet_id = "1-Ic6tHRwEZ2CwD2UYq2gm2NNPfT6NHavHBDibgNFiqo"

    # Read the spreadsheet
    spreadsheet = read_spreadsheet(spreadsheet_id)

    if spreadsheet:
        # Get the first worksheet
        worksheet = spreadsheet.sheet1

        # Example email
        new_email = "Kunaguero@gmail.com"

        # Add the email to the sheet
        add_email(new_email, worksheet)

