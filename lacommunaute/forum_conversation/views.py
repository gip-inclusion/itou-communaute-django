from django.urls import reverse
from machina.apps.forum_conversation import views


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            "forum:forum",
            kwargs={
                "pk": self.forum_post.topic.forum.pk,
                "slug": self.forum_post.topic.forum.slug,
            },
        )


class SuccessUrlWithPostIdMixin:
    def get_success_url(self):
        return (
            reverse(
                "forum:forum",
                kwargs={
                    "pk": self.forum_post.topic.forum.pk,
                    "slug": self.forum_post.topic.forum.slug,
                },
            )
            + f"?post%{self.forum_post.pk}#{self.forum_post.pk}"
        )


class TopicCreateView(SuccessUrlMixin, views.TopicCreateView):
    pass


class TopicUpdateView(SuccessUrlWithPostIdMixin, views.TopicUpdateView):
    pass


class PostCreateView(SuccessUrlWithPostIdMixin, views.PostCreateView):
    pass


class PostUpdateView(SuccessUrlWithPostIdMixin, views.PostUpdateView):
    pass
