from django.contrib.flatpages.models import FlatPage
from django.contrib.sitemaps import Sitemap
from django.db.models.base import Model
from django.urls import reverse

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Topic


class PagesSitemap(Sitemap):
    def items(self):
        return FlatPage.objects.filter(registration_required=False).order_by("title")

    def location(self, obj: Model) -> str:
        return super().location(obj).replace("/flatpages/", "/")

    def changefreq(self, obj: Model) -> str:
        return "weekly"


class ForumSitemap(Sitemap):
    def items(self):
        return Forum.objects.public().order_by("id")

    def location(self, obj: Model) -> str:
        return reverse("forum_extension:forum", kwargs={"pk": obj.pk, "slug": obj.slug})

    def lastmod(self, obj: Model) -> str:
        return obj.last_post_on


class TopicSitemap(Sitemap):
    def items(self):
        return Topic.objects.exclude(approved=False).filter(forum__in=Forum.objects.public()).order_by("-last_post_on")

    def lastmod(self, obj: Model) -> str:
        return obj.last_post_on
