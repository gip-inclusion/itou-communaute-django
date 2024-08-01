import logging
from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import TemplateView

from lacommunaute.event.models import Event
from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Topic


logger = logging.getLogger(__name__)


class LandingPagesListView(UserPassesTestMixin, TemplateView):
    template_name = "pages/landing_pages.html"

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["topics_public"] = Topic.objects.filter(forum__kind=ForumKind.PUBLIC_FORUM, approved=True).order_by(
            "-created"
        )[:4]
        context["forums_category"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, parent__type=1).order_by(
            "-updated"
        )[:4]
        context["forum"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, lft=1, level=0).first()
        context["upcoming_events"] = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:4]
        return context


class HomeWithSearchView(TemplateView):
    template_name = "pages/home_with_search.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["forums_category"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, parent__type=1).order_by(
            "-updated"
        )[:4]
        context["forum"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, lft=1, level=0).first()
        context["upcoming_events"] = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:4]
        return context


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def mentions_legales(request):
    return render(request, "pages/mentions_legales.html")


def politique_de_confidentialite(request):
    return render(request, "pages/politique_de_confidentialite.html")
