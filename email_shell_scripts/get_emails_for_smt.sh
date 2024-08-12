#!/bin/bash

log_file="/home/coboit/thetitandev.com/email_scripts.log"

source /home/coboit/thetitandev.com/venv/bin/activate

echo "[$(date +"%Y-%m-%d %H:%M:%S")] running the SMT script." | tee -a "$log_file"
/home/coboit/thetitandev.com/venv/bin/python /home/coboit/thetitandev.com/get_emails_for_smt.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done running the SMT script." | tee -a "$log_file"

deactivate
