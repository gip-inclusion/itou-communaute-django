#!/bin/sh
set -e

while ! pg_isready -h $PGHOST -p 5432; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 1
done

>&2 echo "Postgres is up - continuing"

python3 -m venv ~/venv
. ~/venv/bin/activate
pip install -r /app/requirements/dev.txt
python manage.py migrate

# --nopin disables for you the annoying PIN security prompt on the web
# debugger. For local dev only of course!
python manage.py runserver_plus 0.0.0.0:8000 --nopin

exec "$@"
