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
docker exec -ti commu_postgres dropdb $POSTGRESQL_ADDON_DB -U $POSTGRES_USER --if-exists --echo

echo "creating new db"
docker exec -ti commu_postgres createdb $POSTGRESQL_ADDON_DB -O $POSTGRES_USER -U $POSTGRES_USER --echo

echo "restoring db"
docker exec -ti commu_postgres pg_restore -U $POSTGRES_USER --dbname=$POSTGRESQL_ADDON_DB --format=c --clean --no-owner --verbose /backups/$DB_BACKUP_NAME

echo "restarting db"
docker-compose down; docker-compose up postgres -d

echo "faking password"
python manage.py set_fake_passwords

echo "import is over"
echo "**************"


