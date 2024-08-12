import gspread
import time
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


# Function to add data to the spreadsheet
def add_data(data, worksheet):
    # Append the data to the sheet
    worksheet.append_row(data)
    print("Data added successfully.")

def add_multiple_data(data_list, worksheet, column_numbers,existing_data = None):

    try:
        # Get all values in the specified columns (excluding header row)
        if not existing_data:
            existing_data = worksheet.get_all_values()[1:]

        # Check if the data already exists in any of the specified columns
        for existing_row in existing_data:
            exists = True
            for col_num, existing_value in zip(column_numbers, existing_row):
                if existing_value != data_list[col_num]:
                    exists = False
                    break
            if exists:
                print("Data already exists in the spreadsheet. Not adding duplicate.")
                return

        # Append the data to the sheet
        worksheet.append_row(data_list)
        print("Data added successfully.")
    except Exception as e:
        if e.response.status_code == 429 and 'RATE_LIMIT_EXCEEDED' in e.response.text:
            print("Rate limit exceeded. Retrying after delay...")
            # Wait for some time before retrying (you may adjust the delay as needed)
            time.sleep(10)  # Example: wait for 10 seconds before retrying
            # Retry the operation recursively
            add_multiple_data(data_list, worksheet, column_numbers)
        else:
            # For other types of API errors, re-raise the exception
            raise


def get_existing_data(worksheet):
    return worksheet.get_all_values()[1:]

# Function to get all data in specified columns
def get_all_data(worksheet, column_numbers):
    # Get all values in the specified columns
    all_data = []
    for column_number in column_numbers:
        column_data = worksheet.col_values(column_number)  # Exclude header row
        all_data.append(column_data)
    return all_data


if __name__ == "__main__":
    # Example spreadsheet ID
    # spreadsheet_id = "1-Ic6tHRwEZ2CwD2UYq2gm2NNPfT6NHavHBDibgNFiqo"
    spreadsheet_id = "1avrcBD_FdtXZrvXwYe-mLU041EgQcCH9LuuAOShKF-w"

    # Read the spreadsheet
    spreadsheet = read_spreadsheet(spreadsheet_id)

    if spreadsheet:
        # Get the first worksheet
        worksheet = spreadsheet.sheet1

        # Example email
        # new_email = "Kunaguero@gmail.com"

        # # Add the email to the sheet
        # add_email(new_email, worksheet)

        add_multiple_data(["jackshukhla@798gmail.com","jackshukla798@gmail.com"], worksheet,[0,1])

