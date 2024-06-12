from django.conf import settings

from lacommunaute.forum.models import Forum


def expose_settings(request):
    """
    Put things into the context to make them available in templates.
    https://docs.djangoproject.com/en/4.1/ref/templates/api/#using-requestcontext
    """
    base_template = "layouts/base_htmx.html" if getattr(request, "htmx", False) else "layouts/base.html"

    return {
        "BASE_TEMPLATE": base_template,
        "MATOMO_SITE_ID": settings.MATOMO_SITE_ID,
        "MATOMO_BASE_URL": settings.MATOMO_BASE_URL,
        "TOOLBOX_FORUM_URL": (
            Forum.objects.get(pk=settings.TOOLBOX_FORUM_ID).get_absolute_url() if settings.TOOLBOX_FORUM_ID else None
        ),
    }
