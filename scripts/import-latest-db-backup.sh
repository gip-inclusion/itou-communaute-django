#!/bin/bash

# PLEASE RUN THIS SCRIPT WITH:
# make postgres_restore_latest_backup

source .envrc

# Restore the latest database dump kept on Scaleway to the local database.
# Default database is $PGDATABASE but you can add a positional argument to change it.
# For example: `./scripts/import-latest-db-backup.sh communaute-real-world
# Make sure you installed the `itou-backups` project before. Also, check that a database server is running.
# $PATH_TO_BACKUPS is mandatory.

if [ ! -f "$PATH_TO_BACKUPS/.env" ]; then
    echo "Backups .env file not found. Stopping here."
    exit 0
fi

# https://www.shellcheck.net/wiki/SC1091
# shellcheck disable=SC1091
source "$PATH_TO_BACKUPS/.env"

db_name="${1:-$PGDATABASE}"
backup_folder="${PATH_TO_BACKUPS}/backups/communaute"
export RCLONE_CONFIG=${RCLONE_CONFIG:-"$PATH_TO_BACKUPS/rclone.conf"}

rclone_last_backup="$(rclone lsf --files-only --max-age 24h communaute:/encrypted-backups)"
rclone copy --max-age 24h --progress "communaute:/encrypted-backups/${rclone_last_backup}" "$backup_folder"
backup_file="${backup_folder}/${rclone_last_backup}"
echo "Restoring ${backup_file} to ${db_name} database"
pg_restore --dbname="${db_name}" --format=c --clean --no-owner --jobs="$(nproc --all --ignore=1)" --verbose "${backup_file}"
# Make sure we don't keep a copy for too long.
rm "$backup_file"
echo "Restoration is over!"

echo "applying new migrations"
python manage.py migrate

echo "faking password"
python manage.py set_fake_passwords

echo "import is over"
echo "**************"
