#!/bin/bash

log_file="/home/coboit/smartysync.com/email_scripts_sap_india.log"

source /home/coboit/smartysync.com/venv/bin/activate

echo "[$(date +"%Y-%m-%d %H:%M:%S")] running the SAP script." | tee -a "$log_file"
/home/coboit/smartysync.com/venv/bin/python /home/coboit/smartysync.com/get_emails_for_sap_india.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done running the SAP script." | tee -a "$log_file"

deactivate