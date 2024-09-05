from django.contrib.flatpages.models import FlatPage
from django.contrib.sitemaps import Sitemap
from django.db.models.base import Model
from django.urls import reverse

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.partner.models import Partner


class PagesSitemap(Sitemap):
    def items(self):
        return FlatPage.objects.filter(registration_required=False).order_by("title")

    def location(self, obj: Model) -> str:
        return super().location(obj).replace("/flatpages/", "/")

    def changefreq(self, obj: Model) -> str:
        return "weekly"


class ForumSitemap(Sitemap):
    def items(self):
        return Forum.objects.all().order_by("id")

    def location(self, obj: Model) -> str:
        return reverse("forum_extension:forum", kwargs={"pk": obj.pk, "slug": obj.slug})

    def lastmod(self, obj: Model) -> str:
        return obj.updated


class TopicSitemap(Sitemap):
    def items(self):
        return Topic.objects.exclude(approved=False).order_by("-last_post_on")

    def lastmod(self, obj: Model) -> str:
        return obj.last_post_on


class PartnerSitemap(Sitemap):
    def items(self):
        return Partner.objects.all()

    def location(self, obj: Model) -> str:
        return reverse("partner:detail", kwargs={"slug": obj.slug, "pk": obj.pk})

    def lastmod(self, obj: Model) -> str:
        return obj.updated
