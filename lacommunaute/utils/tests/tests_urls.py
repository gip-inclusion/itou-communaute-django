import sys

import pytest
from django.urls import NoReverseMatch, clear_url_caches, reverse


@pytest.fixture(autouse=True)
def _clear_url_caches():
    clear_url_caches()
    # The module content depends on the settings, force tests to reimport it.
    sys.modules.pop("config.urls", None)


def test_django_urls_dev(settings):
    settings.DEBUG = True
    assert reverse("login") == "/login/"
    assert reverse("djdt:render_panel") == "/__debug__/render_panel/"


def test_django_urls_prod(settings):
    settings.DEBUG = False
    with pytest.raises(NoReverseMatch):
        reverse("login")
    with pytest.raises(NoReverseMatch):
        reverse("djdt:render_panel")
