from django.conf import settings


def get_absolute_url(path=""):
    if path.startswith("/"):
        path = path[1:]
    return f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}/{path}"
