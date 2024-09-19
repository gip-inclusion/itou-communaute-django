import logging

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import UpdateView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.loading import get_class

from lacommunaute.forum.forms import ForumForm
from lacommunaute.forum.models import Forum, ForumRating
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.view_mixins import FilteredTopicsListViewMixin
from lacommunaute.forum_upvote.models import UpVote


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class ForumView(BaseForumView, FilteredTopicsListViewMixin):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_template_names(self):
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["forum_conversation/topic_list.html"]
        return ["forum/forum_detail.html"]

    def get_queryset(self):
        return self.filter_queryset(self.get_forum().topics.optimized_for_topics_list(self.request.user.id))

    def get_context_data(self, **kwargs):
        forum = self.get_forum()

        if self.request.user.is_authenticated:
            forum.has_upvoted = UpVote.objects.filter(
                object_id=forum.id,
                voter=self.request.user,
                content_type_id=ContentType.objects.get_for_model(forum).id,
            ).exists()

        context = super().get_context_data(**kwargs)
        context["forum"] = forum
        context["FORUM_NUMBER_POSTS_PER_TOPIC"] = settings.FORUM_NUMBER_POSTS_PER_TOPIC
        context["next_url"] = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        context["loadmoretopic_url"] = self.get_load_more_url(
            reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        )
        context["loadmoretopic_suffix"] = "topicsinforum"
        context["form"] = PostForm(forum=forum, user=self.request.user)

        context["rating"] = forum.get_session_rating(self.request.session.session_key)

        context["filter_dropdown_endpoint"] = (
            None
            if self.request.GET.get("page")
            else reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        )
        context = context | self.get_topic_filter_context()

        if forum.image:
            context["og_image"] = forum.image
        return context


class ForumUpdateView(UserPassesTestMixin, UpdateView):
    template_name = "forum/forum_create_or_update.html"
    form_class = ForumForm
    model = Forum

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Mettre à jour le forum {self.object.name}"
        context["back_url"] = reverse("forum_extension:forum", kwargs={"pk": self.object.pk, "slug": self.object.slug})
        return context


class ForumRatingView(View):
    def post(self, request, *args, **kwargs):
        forum_rating = ForumRating.objects.create(
            forum=get_object_or_404(Forum, pk=self.kwargs["pk"]),
            user=request.user if request.user.is_authenticated else None,
            rating=int(request.POST["rating"]),
            session_id=request.session.session_key,
        )

        return render(
            request,
            "forum/partials/rating.html",
            context={"forum": forum_rating.forum, "rating": forum_rating.rating},
        )
