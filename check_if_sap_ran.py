from datetime import datetime  
import re 
import get_emails_for_sap as sap

def get_date(input_text):
    pattern = re.compile(r"\[[^\]]*\]")
    return pattern.match(input_text)

def use_regex(input_text):
    pattern = re.compile(r"\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,3})?\] ([A-Za-z]+( [A-Za-z]+)+)\.", re.IGNORECASE)
    return pattern.match(input_text)

def read_log_file_and_return_lines(filename) -> list:
    with open(filename) as f:
        lines = f.readlines()
        return lines
    
def main():
    filename = 'email_scripts.log'
    lines = read_log_file_and_return_lines(filename)
    lines = lines.reverse()  # 
    line_index = 0

    while True:
        line = lines[line_index]
        match = use_regex(line)
        if match:
            break
        line_index += 1

    if "Successfuly sent the campaign" in lines[line_index + 1]:
        print("Script was succesful.")
        return
    
    sap.main()
    
    

