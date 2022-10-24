from django.conf import settings


def get_absolute_url(path=""):
    if path.startswith("/"):
        path = path[1:]
    return f"{settings.ITOU_PROTOCOL}://{settings.ITOU_FQDN}/{path}"
