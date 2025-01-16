from urllib.parse import urlsplit, urlunsplit

from django import template
from django.http import QueryDict

from lacommunaute.users.enums import IdentityProvider


register = template.Library()


@register.simple_tag
def url_add_query(url, **kwargs):
    """
    Append a querystring param to the given url.
    If the querystring param is already present it will be replaced
    otherwise it will be appended.

    Usage:
        {% load url_query_tags %}
        {% url_add_query request.get_full_path page=2 %}
    """
    parsed = urlsplit(url)
    querystring = QueryDict(parsed.query, mutable=True)
    for item in kwargs:
        if item in querystring:
            querystring.pop(item)
    querystring.update(kwargs)
    return urlunsplit(parsed._replace(query=querystring.urlencode()))


@register.simple_tag
def autologin_proconnect(url, user):
    if user.is_authenticated and user.identity_provider == IdentityProvider.PRO_CONNECT:
        return url_add_query(url, proconnect_login="true", username=user.username)
    return url
