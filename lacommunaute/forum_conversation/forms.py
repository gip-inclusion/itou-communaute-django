from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.forms import CharField, CheckboxSelectMultiple, HiddenInput, ModelMultipleChoiceField
from machina.apps.forum_conversation.forms import PostForm as AbstractPostForm, TopicForm as AbstractTopicForm
from machina.conf import settings as machina_settings
from taggit.models import Tag

from lacommunaute.notification.utils import should_not_be_approved


class PostForm(AbstractPostForm):
    subject = CharField(widget=HiddenInput(), required=False)

    def create_post(self):
        post = super().create_post()
        post.subject = f"{machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX} {self.topic.subject}"

        if self.user.is_anonymous:
            if should_not_be_approved(self.cleaned_data["username"]):
                post.approved = False

        return post

    def update_post(self, post):
        if self.user.is_anonymous:
            post.username = self.cleaned_data["username"]
            if should_not_be_approved(self.cleaned_data["username"]):
                post.approved = False
        else:
            post.updated_by = self.user
        post.updates_count = F("updates_count") + 1


class TopicForm(AbstractTopicForm):
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
        post.topic.save()
        return post
