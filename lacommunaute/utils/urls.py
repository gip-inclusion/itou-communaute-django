import re

from django.conf import settings
from django.utils.functional import keep_lazy_text
from django.utils.html import Urlizer as BaseUrlizer
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.regex_helper import _lazy_re_compile


class Urlizer(BaseUrlizer):
    """
    override django.utils.html.Urlizer to fix conflict between markdown and urlize
    """

    # do not split string from its leading/trailing double quote,
    # to keep markdown link rendered in html (src="www.example.com" and href="www.example.com")
    word_split_re = _lazy_re_compile(r"""([\s<>']+)""")

    # do not consider string containing src= or href= as url
    simple_url_2_re = _lazy_re_compile(
        r"^www\.|^(?!http|src=|href=)\w[^@]+\.(com|edu|gov|int|mil|net|org|fr)($|/.*)$", re.IGNORECASE
    )


urlizer = Urlizer()


@keep_lazy_text
def urlize(text, trim_url_limit=None, nofollow=False, autoescape=False):
    return urlizer(text, trim_url_limit=trim_url_limit, nofollow=nofollow, autoescape=autoescape)


def get_safe_url(request, param_name=None, fallback_url=None, url=None):

    url = url or request.GET.get(param_name) or request.POST.get(param_name)

    allowed_hosts = settings.ALLOWED_HOSTS
    require_https = request.is_secure()

    if url:

        if settings.DEBUG:
            # In DEBUG mode the network location part `127.0.0.1:8000` contains
            # a port and fails the validation of `url_has_allowed_host_and_scheme`
            # since it's not a member of `allowed_hosts`:
            # https://github.com/django/django/blob/525274f/django/utils/http.py#L413
            # As a quick fix, we build a new URL without the port.
            from urllib.parse import ParseResult, urlparse

            url_info = urlparse(url)
            url_without_port = ParseResult(
                scheme=url_info.scheme,
                netloc=url_info.hostname,
                path=url_info.path,
                params=url_info.params,
                query=url_info.query,
                fragment=url_info.fragment,
            ).geturl()
            if url_has_allowed_host_and_scheme(url_without_port, allowed_hosts, require_https):
                return url

        else:
            if url_has_allowed_host_and_scheme(url, allowed_hosts, require_https):
                return url

    return fallback_url
