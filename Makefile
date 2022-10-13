ifeq ($(USE_POETRY),1)
	EXEC_CMD := poetry run
else
	EXEC_CMD :=
endif

.PHONY: console migrate migrations server rebuild_index

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

rebuild_index:
	$(EXEC_CMD) python manage.py rebuild_index

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality fix pylint black flake8 isort
quality:
	$(EXEC_CMD) black --check lacommunaute
	$(EXEC_CMD) isort --check lacommunaute
	$(EXEC_CMD) flake8 lacommunaute --count --show-source --statistics

fix:
	$(EXEC_CMD) black lacommunaute
	$(EXEC_CMD) isort lacommunaute
	$(EXEC_CMD) flake8 lacommunaute

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
