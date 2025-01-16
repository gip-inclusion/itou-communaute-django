import pytest
from django.test import override_settings

from lacommunaute.utils.enums import Environment


@pytest.mark.parametrize(
    "env,expected",
    [
        (Environment.PROD, False),
        (Environment.TEST, False),
        (Environment.DEV, True),
    ],
)
def test_prod_environment(client, db, env, expected):
    with override_settings(ENVIRONMENT=env):
        response = client.get("/")
    assert ('id="debug-mode-banner"' in response.content.decode()) == expected


def test_exposed_settings(client, db):
    response = client.get("/")
    assert "BASE_TEMPLATE" in response.context
    assert "MATOMO_SITE_ID" in response.context
    assert "MATOMO_BASE_URL" in response.context
    assert "ENVIRONMENT" in response.context
    assert "EMPLOIS_PRESCRIBER_SEARCH" in response.context
    assert "EMPLOIS_COMPANY_SEARCH" in response.context
