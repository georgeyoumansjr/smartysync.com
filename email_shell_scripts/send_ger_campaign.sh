#!/bin/bash

log_file="/home/coboit/thetitandev.com/email_scripts.log"

source /home/coboit/thetitandev.com/venv/bin/activate

echo "[$(date +"%Y-%m-%d %H:%M:%S")] running the GER script." | tee -a "$log_file"
/home/coboit/thetitandev.com/venv/bin/python /home/coboit/thetitandev.com/send_ger_campaign.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done running the GER script." | tee -a "$log_file"

deactivate
