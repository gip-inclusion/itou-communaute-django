import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.views.generic import FormView, ListView, TemplateView
from machina.core.db.models import get_model

from lacommunaute.utils.urls import get_safe_url
from lacommunaute.www.forum_member.forms import JoinForumForm


logger = logging.getLogger(__name__)


ForumProfile = get_model("forum_member", "ForumProfile")
Forum = get_model("forum", "Forum")


class ForumProfileListView(ListView):
    model = ForumProfile
    template_name = "forum_member/profiles.html"
    context_object_name = "forum_profiles"


class JoinForumLandingView(TemplateView):

    template_name = "forum_member/join_forum_landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = {
            "previous_url": reverse_lazy("members:join_forum_landing"),
            "next_url": get_safe_url(self.request, "next"),
        }
        context["inclusion_connect_url"] = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"
        return context


class JoinForumFormView(LoginRequiredMixin, FormView):

    login_url = reverse_lazy("members:join_forum_landing")
    template_name = "forum_member/join_forum_form.html"
    form_class = JoinForumForm

    success_url = "/"  # TODO: set target forum URL

    def form_valid(self, form):
        form.join_forum()
        return super().form_valid(form)
