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
