import logging

from django.conf import settings
from django.db.models import OuterRef, Prefetch, Q, Subquery
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.db.models import get_model


logger = logging.getLogger(__name__)

Topic = get_model("forum_conversation", "Topic")
Post = get_model("forum_conversation", "Post")


class ForumView(BaseForumView):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        self.forum = self.get_forum()

        # use slicing ([:1]) instead on .first() methode to get a queryset.
        newest_sq = Post.objects.filter(topic=OuterRef("topic"), approved=True).values("id").order_by("created")[:1]
        latest_sq = (
            Post.objects.filter(topic=OuterRef("topic"), approved=True)
            .values("id")
            .order_by("-created")[: settings.FORUM_NUMBER_POSTS_PER_TOPIC]
        )
        posts = (
            Post.objects.filter(topic__forum=self.forum)
            .exclude(topic__type=Topic.TOPIC_ANNOUNCE)
            .exclude(topic__approved=False)
            .filter(Q(id__in=Subquery(newest_sq)) | Q(id__in=Subquery(latest_sq)))
            .order_by("topic", "created")
            .select_related("poster", "poster__forum_profile")
            .prefetch_related("attachments")
        )
        return (
            self.forum.topics.exclude(type=Topic.TOPIC_ANNOUNCE)
            .exclude(approved=False)
            .prefetch_related(Prefetch("posts", queryset=posts))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["FORUM_NUMBER_POSTS_PER_TOPIC"] = settings.FORUM_NUMBER_POSTS_PER_TOPIC
        return context
