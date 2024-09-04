import pytest  # noqa F401
from django.contrib.flatpages.models import FlatPage
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.partner.factories import PartnerFactory


def test_sitemap(client, db):
    url = reverse("pages:django.contrib.sitemaps.views.sitemap")
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/xml"
    assert "sitemap.xml" in response.templates[0].name


@pytest.mark.parametrize(
    "factory, factory_kwargs,lastmod_field",
    [
        (TopicFactory, {"with_post": True}, "last_post_on"),
        (ForumFactory, {}, "updated"),
        (PartnerFactory, {}, "updated"),
    ],
)
def test_objects_are_in_sitemap(client, db, factory, factory_kwargs, lastmod_field):
    obj = factory(**factory_kwargs)
    response = client.get(reverse("pages:django.contrib.sitemaps.views.sitemap"))

    assert response.status_code == 200
    assert obj.get_absolute_url() in response.content.decode()
    assert f"<lastmod>{getattr(obj, lastmod_field).strftime('%Y-%m-%d')}</lastmod>" in response.content.decode()


def test_flatpage_is_in_sitemap(client, db):
    page = FlatPage.objects.create(title="test", url="/test/", content="test")
    url = reverse("pages:django.contrib.sitemaps.views.sitemap")
    response = client.get(url)
    assert response.status_code == 200
    assert page.url in response.content.decode()
