import logging

from django.views.generic import ListView
from machina.core.db.models import get_model


logger = logging.getLogger(__name__)


ForumProfile = get_model("forum_member", "ForumProfile")
Forum = get_model("forum", "Forum")


class ForumProfileListView(ListView):
    model = ForumProfile
    template_name = "forum_member/profiles.html"
    context_object_name = "forum_profiles"
