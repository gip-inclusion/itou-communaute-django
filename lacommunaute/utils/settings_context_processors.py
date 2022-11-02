from django.conf import settings


def expose_settings(request):
    """
    Put things into the context to make them available in templates.
    https://docs.djangoproject.com/en/4.1/ref/templates/api/#using-requestcontext
    """

    return {
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "COMMU_ENVIRONMENT": settings.COMMU_ENVIRONMENT,
        "COMMU_FQDN": settings.COMMU_FQDN,
    }
