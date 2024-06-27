#!/bin/bash -l

# Variation of a cronjob which sends notifications that have been marked to send ASAP

#
# About clever cloud cronjobs:
# https://next-www.cleverapps.io/doc/administrate/cron/
#

if [[ "$INSTANCE_NUMBER" != "0" ]]; then
    echo "Instance number is ${INSTANCE_NUMBER}. Stop here."
    exit 0
fi

# $APP_HOME is set by default by clever cloud.
cd $APP_HOME

python manage.py send_messages_notifications asap
