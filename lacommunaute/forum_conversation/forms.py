from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.forms import CharField, CheckboxSelectMultiple, HiddenInput, ModelMultipleChoiceField
from machina.apps.forum_conversation.forms import PostForm as AbstractPostForm, TopicForm as AbstractTopicForm
from machina.conf import settings as machina_settings
from taggit.models import Tag

from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.models import BlockedPost
from lacommunaute.forum_moderation.utils import check_post_approbation


class CreateUpdatePostMixin:
    def clean(self):
        cleaned_data = super().clean()
        if "content" in cleaned_data:
            post = check_post_approbation(
                Post(username=cleaned_data.get("username"), content=cleaned_data.get("content"))
            )
            if not post.approved:
                self.add_error(None, "Votre message ne respecte pas les règles de la communauté.")

                if self.user.is_authenticated:
                    post.poster = self.user

                blocked_reason = BlockedPostReason.from_label(post.update_reason)
                if blocked_reason in BlockedPostReason.reasons_tracked_for_stats():
                    BlockedPost.create_from_post(post, blocked_reason)
        return cleaned_data

    def update_post(self, post):
        if self.user.is_anonymous:
            post.username = self.cleaned_data["username"]
        else:
            post.updated_by = self.user

        post.updates_count = F("updates_count") + 1


class PostForm(CreateUpdatePostMixin, AbstractPostForm):
    subject = CharField(widget=HiddenInput(), required=False)

    def create_post(self):
        post = super().create_post()
        post.subject = f"{machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX} {self.topic.subject}"

        if self.user.is_anonymous:
            post.username = self.cleaned_data["username"]

        return post


class TopicForm(CreateUpdatePostMixin, AbstractTopicForm):
    tags = ModelMultipleChoiceField(
        label="", queryset=Tag.objects.all(), widget=CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if hasattr(self.instance, "topic"):
                self.fields["tags"].initial = self.instance.topic.tags.all()
        except ObjectDoesNotExist:
            pass

    def save(self):
        post = super().save()
        post.topic.tags.set(self.cleaned_data["tags"])

        if self.user.is_anonymous:
            post.username = self.cleaned_data["username"]

        post.save()

        return post
