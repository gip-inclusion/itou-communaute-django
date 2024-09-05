import logging

from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum_member.views import (
    ForumProfileDetailView as BaseForumProfileDetailView,
    ForumProfileUpdateView as BaseForumProfileUpdateView,
)
from machina.core.loading import get_class

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
