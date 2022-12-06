import logging

from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlencode
from machina.apps.forum_conversation import views


# from machina.core.db.models import get_model


logger = logging.getLogger(__name__)

# Topic = get_model("forum_conversation", "Topic")


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


class TopicView(views.TopicView):
    def get_topic(self):
        self.topic = super().get_topic()
        self.topic.has_liked = self.topic.likers.filter(id=self.request.user.id).exists()
        self.topic.likes = self.topic.likers.count()
        return self.topic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = {
            "next_url": self.topic.get_absolute_url(),
        }
        context["inclusion_connect_url"] = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"
        return context
