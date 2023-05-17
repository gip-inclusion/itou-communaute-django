import logging

from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one
from lacommunaute.forum_upvote.shortcuts import can_certify_post


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class ForumTopicListView(PermissionRequiredMixin, ListView):
    permission_required = [
        "can_read_forum",
    ]
    template_name = "forum_conversation/topic_list.html"

    paginate_by = paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE
    context_object_name = "topics"

    def get_queryset(self):
        return Topic.objects.filter(forum=self.get_forum()).optimized_for_topics_list(self.request.user.id)

    def get_forum(self):
        if not hasattr(self, "forum"):
            self.forum = get_object_or_404(Forum, pk=self.kwargs["forum_pk"])
        return self.forum

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["forum"] = self.get_forum()
        context["loadmoretopic_url"] = reverse(
            "forum_conversation_extension:topic_list",
            kwargs={"forum_pk": self.forum.pk, "forum_slug": self.forum.slug},
        )
        context["loadmoretopic_suffix"] = "topicsinforum"
        return context

    def get_controlled_object(self):
        return self.get_forum()


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
    template = "forum_conversation/partials/topic_content.html"
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
            self.template,
            context={"topic": topic},
        )

    def get_controlled_object(self):
        return self.get_topic().forum


class TopicCertifiedListView(ListView):
    template_name = "forum_conversation/topic_list.html"

    paginate_by = paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE
    context_object_name = "topics"

    def get_queryset(self):
        return Topic.objects.filter(
            forum__in=Forum.objects.public(), certified_post__isnull=False
        ).optimized_for_topics_list(self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["loadmoretopic_url"] = reverse("forum_conversation_extension:public_certified_topics_list")
        context["loadmoretopic_suffix"] = "certified"
        return context


class TopicCertifiedPostView(TopicContentView):
    template = "forum_conversation/partials/topic_certified_post.html"


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
                "can_certify_post": can_certify_post(self.topic.forum, request.user),
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
