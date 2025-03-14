import logging

from django.shortcuts import get_object_or_404, render
from django.views import View
from machina.core.loading import get_class

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import CertifiedPost, Post, Topic
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one
from lacommunaute.notification.models import Notification


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class TopicContentView(PermissionRequiredMixin, View):
    template = "partials/rendered_md.html"
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

    def get_content(self):
        return self.get_topic().first_post.content

    def get(self, request, **kwargs):
        topic = self.get_topic()

        track_handler.mark_topic_read(topic, request.user)

        return render(
            request,
            self.template,
            context={"content": self.get_content()},
        )

    def get_controlled_object(self):
        return self.get_topic().forum


class TopicCertifiedPostView(TopicContentView):
    def get_content(self):
        return self.get_topic().certified_post.post.content


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
        if request.user.is_authenticated:
            Notification.objects.mark_topic_posts_read(topic, request.user)

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
            post.save()

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

        return render(
            request,
            "forum_conversation/partials/post_feed_form_errors.html",
            context={"topic": self.topic, "post_form": form},
        )

    def get_controlled_object(self):
        return self.get_topic()

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_add_post(obj, user)


class CertifiedPostView(PermissionRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return self.http_method_not_allowed(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = get_object_or_404(
                Post,
                pk=self.request.POST["post_pk"],
            )
        return self.object

    def post(self, request, **kwargs):
        post = self.get_object()
        certified_post = CertifiedPost.objects.filter(post=post)

        if certified_post.exists():
            certified_post.delete()
        else:
            CertifiedPost(post=post, topic=post.topic, user=request.user).save()

        track_handler.mark_topic_read(post.topic, request.user)

        return render(
            request,
            "forum_conversation/partials/posts_list.html",
            context={
                "topic": post.topic,
                "posts": get_posts_of_a_topic_except_first_one(post.topic, request.user),
                "form": PostForm(forum=post.topic.forum, user=request.user),
                "next_url": post.topic.get_absolute_url(),
            },
        )

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_read_forum(obj, user) and user and user.is_staff
