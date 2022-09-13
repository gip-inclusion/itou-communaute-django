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
