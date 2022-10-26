import logging

from django.contrib import messages
from django.urls import reverse
from machina.apps.forum_conversation import views


logger = logging.getLogger(__name__)


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            "forum:forum",
            kwargs={
                "pk": self.forum_post.topic.forum.pk,
                "slug": self.forum_post.topic.forum.slug,
            },
        )


class TopicCreateView(SuccessUrlMixin, views.TopicCreateView):
    pass


class TopicUpdateView(SuccessUrlMixin, views.TopicUpdateView):
    pass


class PostCreateView(SuccessUrlMixin, views.PostCreateView):
    pass


class PostUpdateView(SuccessUrlMixin, views.PostUpdateView):
    pass


class PostDeleteView(views.PostDeleteView):
    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse(
            "forum:forum",
            kwargs={
                "slug": self.object.topic.forum.slug,
                "pk": self.object.topic.forum.pk,
            },
        )
