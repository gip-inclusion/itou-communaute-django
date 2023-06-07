import pytest  # noqa F401
from django.urls import reverse


def test_robots_file(client, db):
    url = reverse("pages:robots")
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "text/plain"
    assert "robots.txt" in response.templates[0].name
