import logging

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum_conversation import views
from machina.core.loading import get_class

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.enums import Filters
from lacommunaute.forum_conversation.forms import PostForm, TopicForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one
from lacommunaute.forum_upvote.shortcuts import can_certify_post


logger = logging.getLogger(__name__)

ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")
track_handler = TrackingHandler()


class FormValidMixin:
    def form_valid(self, *args, **kwargs):
        valid = super().form_valid(*args, **kwargs)
        track_handler.mark_topic_read(self.forum_post.topic, self.request.user)
        return valid


class TopicCreateView(FormValidMixin, views.TopicCreateView):
    post_form_class = TopicForm

    def form_valid(self, *args, **kwargs):
        valid = super().form_valid(*args, **kwargs)
        if self.request.user.is_authenticated:
            self.forum_post.topic.likers.add(self.request.user)
        return valid

    def get_success_url(self):
        if not self.forum_post.approved:
            return reverse(
                "forum_extension:forum",
                kwargs={
                    "slug": self.forum_post.topic.forum.slug,
                    "pk": self.forum_post.topic.forum.pk,
                },
            )
        return reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_slug": self.forum_post.topic.forum.slug,
                "forum_pk": self.forum_post.topic.forum.pk,
                "slug": self.forum_post.topic.slug,
                "pk": self.forum_post.topic.pk,
            },
        )


class TopicUpdateView(FormValidMixin, views.TopicUpdateView):
    post_form_class = TopicForm


class PostCreateView(views.PostCreateView):
    def perform_permissions_check(self, user, obj, perms):
        return False


class PostUpdateView(FormValidMixin, views.PostUpdateView):
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
        return ["forum_conversation/topics_public.html"]

    def get_filter(self):
        if not hasattr(self, "filter"):
            self.filter = self.request.GET.get("filter", None)
        return self.filter

    def get_queryset(self):
        qs = Topic.objects.filter(forum__kind=ForumKind.PUBLIC_FORUM).optimized_for_topics_list(self.request.user.id)

        if self.get_filter() == Filters.NEW:
            qs = qs.unanswered()
        elif self.get_filter() == Filters.CERTIFIED:
            qs = qs.filter(certified_post__isnull=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(user=self.request.user)
        context["loadmoretopic_url"] = reverse("forum_conversation_extension:topics")

        if self.get_filter():
            context["loadmoretopic_url"] += f"?filter={self.get_filter()}"

        context["active_filter_name"] = (
            getattr(Filters, self.get_filter(), Filters.ALL).label if self.get_filter() else Filters.ALL.label
        )
        context["display_filter_dropdown"] = False if self.request.GET.get("page") else True

        context["loadmoretopic_suffix"] = "topics"
        context["total"] = self.get_queryset().count()
        context["filters"] = Filters.choices
        context["forum"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, lft=1, level=0).first()

        return context


class NewsFeedTopicListView(TopicListView):
    def get_template_names(self):
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["forum_conversation/topic_list_newsfeed.html"]
        return ["forum_conversation/topics_newsfeed.html"]

    def get_queryset(self):
        return Topic.objects.filter(forum__kind=ForumKind.NEWS)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["loadmoretopic_url"] = reverse("forum_conversation_extension:newsfeed")
        context["loadmoretopic_suffix"] = "newsfeed"
        context["forum"] = None
        return context
