import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum_member.views import (
    ForumProfileDetailView as BaseForumProfileDetailView,
    ForumProfileUpdateView as BaseForumProfileUpdateView,
)
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_member.forms import ForumProfileForm
from lacommunaute.forum_member.models import ForumProfile


logger = logging.getLogger(__name__)


PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class ForumProfileDetailView(BaseForumProfileDetailView):
    slug_field = "username"
    slug_url_kwarg = "username"


class ForumProfileUpdateView(BaseForumProfileUpdateView):
    form_class = ForumProfileForm

    def get_success_url(self):
        return reverse("members:profile", kwargs={"username": self.request.user.username})


class ModeratorProfileListView(PermissionRequiredMixin, ListView):
    model = ForumProfile
    template_name = "forum_member/moderator_profiles.html"
    context_object_name = "forum_profiles"
    paginate_by = 60
    permission_required = ["can_approve_posts"]

    def get_forum(self):
        """Returns the forum to consider."""
        if not hasattr(self, "forum"):
            self.forum = get_object_or_404(Forum, pk=self.kwargs["pk"])
        return self.forum

    def get_queryset(self):
        """Returns the list of items for this view."""
        self.forum = self.get_forum()
        users = self.forum.members_group.user_set.all()
        return ForumProfile.objects.filter(user__in=users).select_related("user").order_by("user__first_name")

    def get_controlled_object(self):
        """Returns the controlled object."""
        return self.get_forum()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forum = self.get_forum()
        context["forum"] = forum
        return context


class SeekersListView(ListView):
    model = ForumProfile
    template_name = "forum_member/seekers_profiles.html"
    context_object_name = "forum_profiles"
    paginate_by = 78

    def get_queryset(self):
        return ForumProfile.objects.exclude(search="NO").order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subtitle"] = "CIP en recherche active de stage ou d'alternance"
        return context
