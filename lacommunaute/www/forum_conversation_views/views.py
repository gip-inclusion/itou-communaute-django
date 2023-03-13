import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from machina.apps.forum_conversation.views import PostCreateView as MachinaPostCreateView
from machina.core.loading import get_class

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.forum_conversation.views import TopicCreateView
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.www.forum_conversation_views.forms import PostJobOfferForm, TopicJobOfferForm


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
        posts = (
            Post.objects.exclude(topic__approved=False)
            .exclude(pk=topic.first_post.pk)
            .filter(topic=topic)
            .order_by("created")
            .select_related("poster", "poster__forum_profile")
            .prefetch_related("attachments")
            .annotate(
                upvotes_count=Count("upvotes"),
                # using user.id instead of user, to manage anonymous user journey
                has_upvoted=Exists(UpVote.objects.filter(post=OuterRef("pk"), voter__id=self.request.user.id)),
            )
        )

        track_handler.mark_topic_read(topic, request.user)

        return render(
            request,
            "forum_conversation/partials/posts_list.html",
            context={
                "topic": topic,
                "posts": posts,
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


class TopicJobOfferCreateView(LoginRequiredMixin, TopicCreateView):
    template_name = "forum_conversation/topic_job_offer_create.html"
    post_form_class = TopicJobOfferForm

    def form_valid(self, post_form, attachment_formset, poll_option_formset, **kwargs):
        valid = super().form_valid(post_form, attachment_formset, poll_option_formset, **kwargs)
        track_handler.mark_topic_read(self.forum_post.topic, self.request.user)
        return valid

    def get_success_url(self):
        url = reverse(
            "forum_extension:forum",
            kwargs={
                "pk": self.forum_post.topic.forum.pk,
                "slug": self.forum_post.topic.forum.slug,
            },
        )
        return url

