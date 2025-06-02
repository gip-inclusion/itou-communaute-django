# Touch
POSTGRESQL_ADDON_HOST ?= localhost
POSTGRESQL_ADDON_PORT ?= 5432
POSTGRESQL_ADDON_DB ?= communaute
POSTGRESQL_ADDON_USER ?= communaute
POSTGRESQL_ADDON_PASSWORD ?= password
POSTGRESQL_ADDON_URI ?= "postgresql://$(POSTGRESQL_ADDON_USER):$(POSTGRESQL_ADDON_PASSWORD)@$(POSTGRESQL_ADDON_HOST):$(POSTGRESQL_ADDON_PORT)/$(POSTGRESQL_ADDON_DB)"

DJLINT_EXCLUDE ?= lacommunaute/templates/middleware/

# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality fix
quality:
	ruff check lacommunaute
	djlint --lint --check lacommunaute --exclude $(DJLINT_EXCLUDE)

fix:
	ruff check --fix lacommunaute
	djlint --reformat lacommunaute

.PHONY: index
index:
	INSTANCE_NUMBER=0 \
	POSTGRESQL_ADDON_URI=$(POSTGRESQL_ADDON_URI) \
	clevercloud/rebuild_index.sh

# DB

.PHONY: resetdb
resetdb:
	dropdb --if-exists $(POSTGRESQL_ADDON_DB)
	createdb $(POSTGRESQL_ADDON_DB)
	python manage.py migrate
	python manage.py populate
