import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import FormView, ListView, TemplateView
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.utils.urls import get_safe_url
from lacommunaute.www.forum_member.forms import JoinForumForm


logger = logging.getLogger(__name__)


ForumProfile = get_model("forum_member", "ForumProfile")
Forum = get_model("forum", "Forum")
PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class ForumProfileListView(ListView):
    model = ForumProfile
    template_name = "forum_member/profiles.html"
    context_object_name = "forum_profiles"


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
        return ForumProfile.objects.filter(user__in=users).order_by("user__first_name")

    def get_controlled_object(self):
        """Returns the controlled object."""
        return self.get_forum()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forum = self.get_forum()
        context["forum"] = forum
        return context


class JoinForumLandingView(TemplateView):

    template_name = "forum_member/join_forum_landing.html"

    def get_forum(self):
        if not hasattr(self, "forum"):
            self.forum = get_object_or_404(
                Forum,
                invitation_token=self.kwargs["token"],
            )
        return self.forum

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forum = self.get_forum()
        context["forum"] = forum
        params = {
            "previous_url": reverse(
                "members:join_forum_landing",
                kwargs={
                    "token": forum.invitation_token,
                },
            ),
            "next_url": get_safe_url(self.request, "next"),
        }
        context["inclusion_connect_url"] = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"
        return context


class JoinForumFormView(LoginRequiredMixin, FormView):

    template_name = "forum_member/join_forum_form.html"
    form_class = JoinForumForm

    def get_forum(self):
        if not hasattr(self, "forum"):
            self.forum = get_object_or_404(
                Forum,
                invitation_token=self.kwargs["token"],
            )
        return self.forum

    def form_valid(self, form):
        form.forum = self.get_forum()
        form.user = self.request.user
        form.join_forum()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["forum"] = self.get_forum()
        return context

    def get_login_url(self):
        return reverse(
            "members:join_forum_landing",
            kwargs={
                "token": self.kwargs["token"],
            },
        )

    def get_success_url(self):
        return reverse(
            "forum:forum",
            kwargs={
                "slug": self.forum.slug,
                "pk": self.forum.pk,
            },
        )
