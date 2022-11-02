ifeq ($(USE_POETRY),1)
	EXEC_CMD := poetry run
else
	EXEC_CMD :=
endif

.PHONY: console migrate migrations server dependencies

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

console:
	$(EXEC_CMD) python manage.py shell

migrate:
	$(EXEC_CMD) python manage.py migrate

migrations:
	$(EXEC_CMD) python manage.py makemigrations

server:
	$(EXEC_CMD) python manage.py runserver

dependencies:
	poetry lock; poetry run poe export; poetry run poe export_dev

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality fix pylint
quality:
	$(EXEC_CMD) black --check lacommunaute
	$(EXEC_CMD) isort --check --profile black lacommunaute
	$(EXEC_CMD) flake8 lacommunaute --count --show-source --statistics

fix:
	$(EXEC_CMD) black lacommunaute
	$(EXEC_CMD) isort --profile black lacommunaute
	$(EXEC_CMD) flake8 lacommunaute
	$(EXEC_CMD) djhtml --in-place $(shell find lacommunaute/templates -name "*.html")

pylint:
	$(EXEC_CMD) pylint lacommunaute


# Docker shell.
# =============================================================================

.PHONY: shell_on_postgres_container

shell_on_postgres_container:
	docker exec -ti postgres /bin/bash


# Postgres CLI.
# =============================================================================

.PHONY: psql

# Connect to the `postgres` container as the POSTGRES_USER user.
psql:
	docker exec -ti -e PGPASSWORD=$(POSTGRES_PASSWORD) commu_postgres psql -U $(POSTGRES_USER)
