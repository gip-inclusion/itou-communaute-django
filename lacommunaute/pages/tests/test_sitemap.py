import pytest  # noqa F401
from django.contrib.flatpages.models import FlatPage
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory


def test_sitemap(client, db):
    url = reverse("pages:django.contrib.sitemaps.views.sitemap")
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/xml"
    assert "sitemap.xml" in response.templates[0].name


def test_topic_is_in_sitemap(client, db):
    topic = TopicFactory()
    url = reverse("pages:django.contrib.sitemaps.views.sitemap")
    response = client.get(url)
    assert response.status_code == 200
    assert topic.get_absolute_url() in response.content.decode()


def test_forum_is_in_sitemap(client, db):
    forum = ForumFactory()
    url = reverse("pages:django.contrib.sitemaps.views.sitemap")
    response = client.get(url)
    assert response.status_code == 200
    assert reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}) in response.content.decode()


def test_flatpage_is_in_sitemap(client, db):
    page = FlatPage.objects.create(title="test", url="/test/", content="test")
    url = reverse("pages:django.contrib.sitemaps.views.sitemap")
    response = client.get(url)
    assert response.status_code == 200
    assert page.url in response.content.decode()
