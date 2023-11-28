#!/bin/bash -l

# Rebuild index for the search engine.
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

python manage.py extract_tables
