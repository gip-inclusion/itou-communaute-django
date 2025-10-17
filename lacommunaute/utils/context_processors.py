from urllib.parse import urlencode

from django.conf import settings


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
        "ENVIRONMENT": settings.ENVIRONMENT,
        "EMPLOIS_PRESCRIBER_SEARCH": settings.EMPLOIS_PRESCRIBER_SEARCH,
        "EMPLOIS_COMPANY_SEARCH": settings.EMPLOIS_COMPANY_SEARCH,
    }



def matomo(request):
    if not request.resolver_match:
        return {"send_to_matomo": False}

    context = {"send_to_matomo": True}
    url = request.resolver_match.route
    # Only keep Matomo-related params for now.
    params = {k: v for k, v in request.GET.lists() if k.startswith(("utm_", "mtm_", "piwik_"))}
    if params:
        url = f"{url}?{urlencode(sorted(params.items()), doseq=True)}"
    context["matomo_custom_url"] = url
    return context
