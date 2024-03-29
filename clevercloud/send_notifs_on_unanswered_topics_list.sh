#!/bin/bash -l

if [ -z "$1" ]; then
  echo "Error: Missing argument. Please provide List ID."
  exit 1
fi

#
# About clever cloud cronjobs:
# https://www.clever-cloud.com/doc/tools/crons/
#

if [[ "$INSTANCE_NUMBER" != "0" ]]; then
    echo "Instance number is ${INSTANCE_NUMBER}. Stop here."
    exit 0
fi

# $APP_HOME is set by default by clever cloud.
cd $APP_HOME

python manage.py send_notifs_on_unanswered_topics --list_id $1
