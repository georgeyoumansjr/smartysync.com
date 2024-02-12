#!/bin/bash

log_file="/home/coboit/thetitandev.com/email_scripts.log"

source /home/coboit/thetitandev.com/venv/bin/activate

echo "[$(date +"%Y-%m-%d %H:%M:%S")] running the TGT script." | tee -a "$log_file"
/home/coboit/thetitandev.com/venv/bin/python /home/coboit/thetitandev.com/get_emails_for_tgt.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done running the TGT script." | tee -a "$log_file"

deactivate
