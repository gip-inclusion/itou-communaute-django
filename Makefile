# QUALITY ASSURANCE
# ~~~~~~~~~~~~~~~~~
# The following rules can be used to check code quality, import sorting, etc.
# --------------------------------------------------------------------------------------------------

.PHONY: quality fix
quality:
	black --check lacommunaute
	ruff check lacommunaute
	djlint --lint --check lacommunaute

fix:
	black lacommunaute
	ruff check --fix lacommunaute
	djlint --reformat lacommunaute

# Whoosh index
# =============================================================================
.PHONY: index

index:
	python manage.py rebuild_index --noinput
