import sys

import pytest
from django.urls import NoReverseMatch, clear_url_caches, reverse

from lacommunaute.utils.urls import clean_next_url


@pytest.fixture(autouse=True)
def _clear_url_caches():
    clear_url_caches()
    # The module content depends on the settings, force tests to reimport it.
    sys.modules.pop("config.urls", None)


def test_django_urls_prod(settings):
    settings.DEBUG = False
    with pytest.raises(NoReverseMatch):
        reverse("djdt:render_panel")


@pytest.mark.parametrize(
    "url, expected", [(None, "/"), ("http://www.unallowed.com", "/"), ("/", "/"), ("/topics/", "/topics/")]
)
def test_clean_next_url(url, expected):
    assert clean_next_url(url) == expected
