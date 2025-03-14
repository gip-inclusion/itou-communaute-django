import logging

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum_conversation import views
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm, TopicForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one
from lacommunaute.forum_conversation.view_mixins import FilteredTopicsListViewMixin
from lacommunaute.notification.models import Notification


logger = logging.getLogger(__name__)

TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")
track_handler = TrackingHandler()


class FormValidMixin:
    def form_valid(self, *args, **kwargs):
        valid = super().form_valid(*args, **kwargs)

        track_handler.mark_topic_read(self.forum_post.topic, self.request.user)
        return valid


class TopicCreateView(FormValidMixin, views.TopicCreateView):
    post_form_class = TopicForm

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
        return topic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.topic.get_absolute_url()
        context["form"] = PostForm(forum=self.topic.forum, user=self.request.user)
        return context

    def get_queryset(self):
        return get_posts_of_a_topic_except_first_one(self.topic, self.request.user)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            Notification.objects.mark_topic_posts_read(self.get_topic(), request.user)
        return super().get(request, *args, **kwargs)


class TopicListView(FilteredTopicsListViewMixin, ListView):
    context_object_name = "topics"
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_template_names(self):
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["forum_conversation/topic_list.html"]
        return ["forum_conversation/topics_public.html"]

    def get_queryset(self):
        return self.filter_queryset(Topic.objects.optimized_for_topics_list(self.request.user.id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(user=self.request.user)

        context["loadmoretopic_url"] = self.get_load_more_url(reverse("forum_conversation_extension:topics"))
        context["filter_dropdown_endpoint"] = (
            None if self.request.GET.get("page") else reverse("forum_conversation_extension:topics")
        )

        context["loadmoretopic_suffix"] = "topics"
        context["forum"] = Forum.objects.get_main_forum()
        context = context | self.get_topic_filter_context()

        return context
