#!/bin/bash

# Path to the .env file
ENV_FILE=".env"

# Define the old and new email addresses and email host
OLD_EMAIL="coboit@prosmartsync.com"
NEW_EMAIL="coboit@smartyswitch.com"
OLD_EMAIL_HOST="mail.prosmartsync.com"
NEW_EMAIL_HOST="mail.smartyswitch.com"

# Function to update the .env file
update_env_file() {
    local OLD_VALUE="$1"
    local NEW_VALUE="$2"
    local KEY="$3"
    
    # Replace old value with new value in the .env file
    sed -i "s/${KEY}=${OLD_VALUE}/${KEY}=${NEW_VALUE}/g" "$ENV_FILE"
    echo "${KEY} updated to ${NEW_VALUE} in .env file"
}

# Check if the .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Get the current values from the .env file
CURRENT_EMAIL=$(grep "^DEFAULT_FROM_EMAIL=" "$ENV_FILE" | cut -d'=' -f2)
CURRENT_EMAIL_HOST=$(grep "^EMAIL_HOST=" "$ENV_FILE" | cut -d'=' -f2)

# Check if the current values match the old values
if [ "$CURRENT_EMAIL" = "$OLD_EMAIL" ]; then
    # Update email address
    update_env_file "$OLD_EMAIL" "$NEW_EMAIL" "DEFAULT_FROM_EMAIL"
    update_env_file "$OLD_EMAIL" "$NEW_EMAIL" "EMAIL_HOST_USER"
    update_env_file "$OLD_EMAIL" "$NEW_EMAIL" "SERVER_EMAIL"
fi

if [ "$CURRENT_EMAIL_HOST" = "$OLD_EMAIL_HOST" ]; then
    # Update email host
    update_env_file "$OLD_EMAIL_HOST" "$NEW_EMAIL_HOST" "EMAIL_HOST"
fi

if [ "$CURRENT_EMAIL" = "$NEW_EMAIL" ]; then
    # Update email address
    update_env_file "$NEW_EMAIL" "$OLD_EMAIL" "DEFAULT_FROM_EMAIL"
    update_env_file "$NEW_EMAIL" "$OLD_EMAIL" "EMAIL_HOST_USER"
    update_env_file "$NEW_EMAIL" "$OLD_EMAIL" "SERVER_EMAIL"
fi

if [ "$CURRENT_EMAIL_HOST" = "$NEW_EMAIL_HOST" ]; then
    # Update email host
    update_env_file "$NEW_EMAIL_HOST" "$OLD_EMAIL_HOST" "EMAIL_HOST"
fi

echo "Email addresses and email host updated successfully!"

sudo systemctl restart gunicorn_smartyswitch

echo "Restarted Gunicorn_smartyswitch"

sudo supervisorctl restart celery_smartyswitch

echo "Restarted celery_smartyswitch"

sudo supervisorctl restart celery_beat_smartyswitch

echo "Restarted celery_beat_smartyswitch"