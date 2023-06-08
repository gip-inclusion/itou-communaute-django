import logging

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum_conversation import views
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.enums import Filters
from lacommunaute.forum_conversation.forms import PostForm, TopicForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one
from lacommunaute.forum_upvote.shortcuts import can_certify_post
from lacommunaute.utils.middleware import store_upper_visible_forums


logger = logging.getLogger(__name__)

ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")
track_handler = TrackingHandler()


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            "forum_extension:forum",
            kwargs={
                "pk": self.forum_post.topic.forum.pk,
                "slug": self.forum_post.topic.forum.slug,
            },
        )


class FormValidMixin:
    def form_valid(self, *args, **kwargs):
        valid = super().form_valid(*args, **kwargs)
        track_handler.mark_topic_read(self.forum_post.topic, self.request.user)
        return valid


class TopicCreateView(SuccessUrlMixin, FormValidMixin, views.TopicCreateView):
    post_form_class = TopicForm

    def form_valid(self, *args, **kwargs):
        valid = super().form_valid(*args, **kwargs)
        if self.request.user.is_authenticated:
            self.forum_post.topic.likers.add(self.request.user)
        if self.forum_post.topic.forum.is_newsfeed:
            self.forum_post.topic.type = Topic.TOPIC_NEWS
            self.forum_post.topic.save()
        return valid


class TopicUpdateView(SuccessUrlMixin, FormValidMixin, views.TopicUpdateView):
    post_form_class = TopicForm


class PostCreateView(views.PostCreateView):
    def perform_permissions_check(self, user, obj, perms):
        return False


class PostUpdateView(SuccessUrlMixin, FormValidMixin, views.PostUpdateView):
    pass


class PostDeleteView(views.PostDeleteView):
    def get_success_url(self):
        messages.success(self.request, self.success_message)

        return reverse(
            "forum_extension:forum",
            kwargs={
                "slug": self.object.topic.forum.slug,
                "pk": self.object.topic.forum.pk,
            },
        )


class TopicView(views.TopicView):
    def get_topic(self):
        topic = super().get_topic()
        topic.has_liked = self.topic.likers.filter(id=self.request.user.id).exists()
        topic.likes = self.topic.likers.count()
        return topic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.topic.get_absolute_url()
        context["form"] = PostForm(forum=self.topic.forum, user=self.request.user)
        context["can_certify_post"] = can_certify_post(self.topic.forum, self.request.user)
        return context

    def get_queryset(self):
        return get_posts_of_a_topic_except_first_one(self.topic, self.request.user)


class TopicListView(ListView):
    context_object_name = "topics"
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_template_names(self):
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["forum_conversation/topic_list.html"]
        return ["pages/home.html"]

    def get_filter(self):
        if not hasattr(self, "filter"):
            self.filter = self.request.GET.get("filter", None)
        return self.filter

    def get_content_tree(self):
        if not hasattr(self, "forum_visibility_content_tree"):
            self.forum_visibility_content_tree = ForumVisibilityContentTree.from_forums(
                self.request.forum_permission_handler.forum_list_filter(
                    Forum.objects.exclude(type=Forum.FORUM_CAT).prefetch_related("members_group__user_set"),
                    self.request.user,
                ),
            )
            store_upper_visible_forums(self.request, self.forum_visibility_content_tree.top_nodes)
        return self.forum_visibility_content_tree

    def get_queryset(self):
        forums = self.get_content_tree().forums
        qs = Topic.objects.filter(forum__in=forums).optimized_for_topics_list(self.request.user.id)

        if self.get_filter() == Filters.NEW:
            qs = qs.unanswered()
        elif self.get_filter() == Filters.CERTIFIED:
            qs = qs.filter(certified_post__isnull=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(user=self.request.user)
        context["loadmoretopic_url"] = reverse("forum_conversation_extension:home")

        if self.get_filter():
            context["loadmoretopic_url"] += f"?filter={self.get_filter()}"

        context["active_filter_name"] = (
            getattr(Filters, self.get_filter(), Filters.ALL).label if self.get_filter() else Filters.ALL.label
        )
        context["display_filter_dropdown"] = False if self.request.GET.get("page") else True

        context["loadmoretopic_suffix"] = "topics"
        context["total"] = self.get_queryset().count()
        context["filters"] = Filters.choices

        return context


class TopicNewsListView(ListView):
    context_object_name = "topics"
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE
    template_name = "forum_conversation/topic_list.html"

    def get_queryset(self):
        return Topic.objects.filter(forum__in=Forum.objects.public(), type=Topic.TOPIC_NEWS).optimized_for_topics_list(
            self.request.user.id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(user=self.request.user)
        context["loadmoretopic_url"] = reverse("forum_conversation_extension:newsfeed_topics_list")
        context["loadmoretopic_suffix"] = "newsfeed"
        context["display_filter_dropdown"] = False
        return context
