#!/bin/bash

log_file="/home/coboit/smartysync.com/sync_unsubscribers.log"

source /home/coboit/smartysync.com/venv/bin/activate

echo "[$(date +"%Y-%m-%d %H:%M:%S")] running the Unsubs sync script." | tee -a "$log_file"
/home/coboit/smartysync.com/venv/bin/python /home/coboit/smartysync.com/upload_rm_unsubscribers.py
echo "[$(date +"%Y-%m-%d %H:%M:%S")] done running the Unsubs script." | tee -a "$log_file"

deactivate
