from django.db.models import F
from django.forms import CharField, HiddenInput
from machina.apps.forum_conversation.forms import PostForm as AbstractPostForm
from machina.conf import settings as machina_settings


class PostForm(AbstractPostForm):
    subject = CharField(widget=HiddenInput(), required=False)

    def create_post(self):
        post = super().create_post()
        post.subject = (
            f"{machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX} {self.topic.subject}"
        )
        return post

    def update_post(self, post):
        if self.user.is_anonymous:
            post.username = self.cleaned_data["username"]
        else:
            post.updated_by = self.user
        post.updates_count = F("updates_count") + 1
