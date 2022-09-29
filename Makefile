ifeq ($(USE_POETRY),1)
	EXEC_CMD := poetry run
else
	EXEC_CMD :=
endif

ifeq ($(DJANGO_SETTINGS_MODULE),)
    SETTINGS :=
else
    SETTINGS := --settings=$(DJANGO_SETTINGS_MODULE)
endif

.PHONY: console migrate migrations server

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

console:
	$(EXEC_CMD) python manage.py shell $(SETTINGS)

migrate:
	$(EXEC_CMD) python manage.py migrate $(SETTINGS)

migrations:
	$(EXEC_CMD) python manage.py makemigrations $(SETTINGS)

server:
	$(EXEC_CMD) python manage.py runserver $(SETTINGS)


# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality pylint black flake8 isort
quality:
	$(EXEC_CMD) black --check lacommunaute
	$(EXEC_CMD) isort --check lacommunaute
	$(EXEC_CMD) flake8 lacommunaute --count --show-source --statistics

pylint:
	$(EXEC_CMD) pylint lacommunaute

black:
	$(EXEC_CMD) black lacommunaute

flake8:
	$(EXEC_CMD) flake8 lacommunaute

isort:
	$(EXEC_CMD) isort lacommunaute

# Docker shell.
# =============================================================================

.PHONY: shell_on_postgres_container

shell_on_postgres_container:
	docker exec -ti postgres /bin/bash


# Postgres CLI.
# =============================================================================

.PHONY: psql psql_root

# Connect to the `postgres` container as the POSTGRES_USER user.
psql:
	docker exec -ti -e PGPASSWORD=$(POSTGRES_PASSWORD) postgres psql -U $(POSTGRES_USER)
