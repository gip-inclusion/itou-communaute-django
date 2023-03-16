import logging

from django.shortcuts import get_object_or_404, render
from django.views import View
from machina.core.loading import get_class

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class TopicLikeView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def post(self, request, **kwargs):
        topic = self.get_topic()

        if not topic.likers.filter(id=request.user.id).exists():
            topic.likers.add(request.user)
            topic.has_liked = True
        else:
            topic.likers.remove(request.user)
            topic.has_liked = False

        topic.save()
        topic.likes = topic.likers.count()

        track_handler.mark_topic_read(topic, request.user)

        return render(request, "forum_conversation/partials/topic_likes.html", context={"topic": topic})

    def get_controlled_object(self):
        return self.get_topic().forum


class TopicContentView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def get(self, request, **kwargs):
        topic = self.get_topic()

        track_handler.mark_topic_read(topic, request.user)

        return render(
            request,
            "forum_conversation/partials/topic_content.html",
            context={"topic": topic},
        )

    def get_controlled_object(self):
        return self.get_topic().forum


class PostListView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def get(self, request, **kwargs):
        topic = self.get_topic()

        track_handler.mark_topic_read(topic, request.user)

        return render(
            request,
            "forum_conversation/partials/posts_list.html",
            context={
                "topic": topic,
                "posts": get_posts_of_a_topic_except_first_one(topic, request.user),
                "form": PostForm(forum=self.topic.forum, user=request.user),
                "next_url": self.topic.get_absolute_url(),
            },
        )

    def get_controlled_object(self):
        return self.get_topic().forum


class PostFeedCreateView(PermissionRequiredMixin, View):
    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def post(self, request, **kwargs):
        kwargs = {
            "user": request.user,
            "forum": self.topic.forum,
            "topic": self.topic,
            "data": self.request.POST,
            "files": self.request.FILES,
        }
        form = PostForm(**kwargs)
        if form.is_valid():
            post = form.save()
            # set count to zero by default. no need to annotate queryset when saving new post
            post.upvotes_count = 0

            track_handler.mark_topic_read(self.topic, request.user)

            return render(
                request,
                "forum_conversation/partials/post_feed.html",
                context={
                    "post": post,
                    "topic": self.topic,
                    "form": PostForm(forum=self.topic.forum, user=request.user),
                },
            )

        return render(request, "500.html", status=500)

    def get_controlled_object(self):
        return self.get_topic()

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_add_post(obj, user)
