import logging

from django.conf import settings
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.db.models import get_model


logger = logging.getLogger(__name__)

Topic = get_model("forum_conversation", "Topic")


class ForumView(BaseForumView):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        """Returns the list of items for this view."""
        self.forum = self.get_forum()
        qs = (
            self.forum.topics.exclude(type=Topic.TOPIC_ANNOUNCE)
            .exclude(approved=False)
            .select_related("poster", "poster__forum_profile")
            .prefetch_related(
                "posts",
                "posts__poster",
                "posts__poster__forum_profile",
                "posts__attachments",
            )
        )
        return qs
