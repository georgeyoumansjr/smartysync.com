#!/bin/bash

log_file="/home/coboit/thetitandev.com/email_scripts.log"

source /home/coboit/thetitandev.com/venv/bin/activate

echo "[$(date +"%Y-%m-%d %H:%M:%S")] running the SAP script." | tee -a "$log_file"
/home/coboit/thetitandev.com/venv/bin/python /home/coboit/thetitandev.com/get_emails_for_sap.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done running the SAP script." | tee -a "$log_file"
/home/coboit/thetitandev.com/venv/bin/python /home/coboit/thetitandev.com/check_if_sap_ran.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done checking the SAP script." | tee -a "$log_file"

deactivate