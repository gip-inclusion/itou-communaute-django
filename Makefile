.PHONY: console migrate migrations server

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

shell:
	python manage.py shell_plus

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

server:
	python manage.py runserver

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality fix pylint test
quality:
	black --check lacommunaute
	ruff check lacommunaute
	djlint --lint --check lacommunaute

fix:
	black lacommunaute
	ruff check --fix lacommunaute
	djlint --reformat lacommunaute

pylint:
	pylint lacommunaute

test:
	pytest --numprocesses=logical --create-db

# Docker shell.
# =============================================================================

.PHONY: shell_on_postgres_container

shell_on_postgres_container:
	docker exec -ti commu_postgres /bin/bash

# Postgres CLI.
# =============================================================================

.PHONY: psql postgres_restore_latest_backup

# Connect to the `postgres` container as the POSTGRES_USER user.
psql:
	docker exec -ti -e PGPASSWORD=$(POSTGRES_PASSWORD) commu_postgres psql -U $(POSTGRES_USER)

# Download last prod backup and inject it locally.
# ----------------------------------------------------
# - Clone the git `itou-backups` project first and run `make build`. https://github.com/betagouv/itou-backups
# - Copy .env.template and set correct values.
# - run `rclone copy --max-age 24h --progress communaute:/encrypted-backups ./backups` to collect last backup

postgres_restore_latest_backup:
	./scripts/import-latest-db-backup.sh

# Whoosh index
# =============================================================================
.PHONY: index

index:
	python manage.py rebuild_index --noinput
