#!/bin/bash

# PLEASE RUN THIS SCRIPT WITH:
# make postgres_restore_latest_backup

source .env

if [ -z $PATH_TO_BACKUPS ]; then
  echo "please add 'PATH_TO_BACKUPS=/your/backups/directory' in .env at the root of the project in order to run this script"
  exit
fi

# Download last available backup
# rclone copy --max-age 24h --progress communaute:/encrypted-backups ./backups
echo "please rclone the last db backup to $PATH_TO_BACKUPS"

# Get the latest backup filename and path
DB_BACKUP_NAME=$(ls $PATH_TO_BACKUPS | tail -n1)
echo "Going to restore $DB_BACKUP_NAME"
DB_BACKUP_PATH=$PATH_TO_BACKUPS/$DB_BACKUP_NAME

echo "Going to inject DB_BACKUP_PATH=$DB_BACKUP_PATH"
docker cp $DB_BACKUP_PATH commu_postgres:/backups

echo "dropping current db"
dropdb $PGDATABASE -U $PGUSER --if-exists --echo

echo "creating new db"
createdb $PGDATABASE -O $PGUSER -U $PGUSER --echo

echo "restoring db"
pg_restore -U $PGUSER --dbname=$PGDATABASE --format=c --clean --no-owner $DB_BACKUP_PATH

echo "applying new migrations"
python manage.py migrate

echo "faking password"
python manage.py set_fake_passwords

echo "import is over"
echo "**************"
