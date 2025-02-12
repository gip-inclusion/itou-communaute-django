import logging
from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import TemplateView

from lacommunaute.event.models import Event
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic


logger = logging.getLogger(__name__)


class LandingPagesListView(UserPassesTestMixin, TemplateView):
    template_name = "pages/landing_pages.html"

    def test_func(self):
        return self.request.user.is_staff


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["forums_category"] = Forum.objects.filter(parent__type=1).order_by("-updated")[:4]
        context["forum"] = Forum.objects.get_main_forum()
        context["upcoming_events"] = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:4]
        context["unanswered_topics"] = Topic.objects.unanswered()[:4]
        context["form"] = PostForm(user=self.request.user)
        return context


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def mentions_legales(request):
    return render(request, "pages/mentions_legales.html")


def politique_de_confidentialite(request):
    return render(request, "pages/politique_de_confidentialite.html")
