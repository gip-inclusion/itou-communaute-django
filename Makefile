PROJECT_NAME := lacommunaute
PROJECT_CONFIGURATION_PACKAGE := config
DJANGO_SETTINGS_MODULE := $(PROJECT_CONFIGURATION_PACKAGE).settings.dev

ifeq ($(GITHUB_ACTIONS),1)
	EXEC_CMD :=
else
	EXEC_CMD := poetry run
endif

init:
	poetry install


.PHONY: c console migrate migrations s server superuser requirements

# DEVELOPMENT
# ~~~~~~~~~~~
# The following rules can be used during development in order to launch development server, generate
# locales, etc.
# --------------------------------------------------------------------------------------------------

c: console
console:
	poetry run python manage.py shell --settings=$(DJANGO_SETTINGS_MODULE)

migrate:
	poetry run python manage.py migrate --settings=$(DJANGO_SETTINGS_MODULE)

migrations:
	poetry run python manage.py makemigrations --settings=$(DJANGO_SETTINGS_MODULE)

s: server
server:
	poetry run python manage.py runserver 127.0.0.1:8000 --settings=$(DJANGO_SETTINGS_MODULE)

superuser:
	poetry run python manage.py createsuperuser --settings=$(DJANGO_SETTINGS_MODULE)

requirements:
	poetry run poe export_dev
	poetry run poe export

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality pylint djhtml black flake8
## Trigger all quality assurance checks.
quality:
	$(EXEC_CMD) black --check $(PROJECT_NAME)
	$(EXEC_CMD) isort --check $(PROJECT_NAME)
## 	$(EXEC_CMD) djhtml --check $(shell find main/templates -name "*.html")
	$(EXEC_CMD) flake8 $(PROJECT_NAME) --count --show-source --statistics

pylint:
	poetry run pylint $(PROJECT_NAME)

black:
	poetry run black $(PROJECT_NAME)

flake8:
	poetry run flake8 $(PROJECT_NAME)

isort:
	poetry run isort $(PROJECT_NAME)

#djhtml:
#	poetry run djhtml -i $(shell find main/templates -name "*.html")

# TESTING
# ~~~~~~~
# The following rules can be used to trigger tests execution and produce coverage reports.
# --------------------------------------------------------------------------------------------------

.PHONY: t tests
## Alias of "tests".
t: tests
## Run the Python test suite.
tests:
	poetry run py.test

.PHONY: coverage
## Collects code coverage data.
coverage:
	poetry run py.test --cov-report term-missing --cov $(PROJECT_NAME)
