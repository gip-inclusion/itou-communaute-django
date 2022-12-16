import logging

from django.conf import settings
from django.db.models import Count, Exists, OuterRef
from django.urls import reverse
from django.utils.http import urlencode
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.db.models import get_model

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.users.models import User


logger = logging.getLogger(__name__)

Topic = get_model("forum_conversation", "Topic")
Post = get_model("forum_conversation", "Post")


class ForumView(BaseForumView):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        self.forum = self.get_forum()

        qs = (
            self.forum.topics.exclude(type=Topic.TOPIC_ANNOUNCE)
            .exclude(approved=False)
            .annotate(likes=Count("likers"))
            .annotate(has_liked=Exists(User.objects.filter(topic_likes=OuterRef("id"), id=self.request.user.id)))
            .select_related(
                "poster",
                "poster__forum_profile",
                "first_post",
            )
            .prefetch_related("poll", "poll__options", "poll__options__votes", "posts", "posts__attachments")
            .order_by("-last_post_on")
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["FORUM_NUMBER_POSTS_PER_TOPIC"] = settings.FORUM_NUMBER_POSTS_PER_TOPIC
        params = {
            "next_url": reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        }
        context["inclusion_connect_url"] = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"
        context["form"] = PostForm(forum=self.forum, user=self.request.user)
        return context
