from django.forms import CharField, HiddenInput
from machina.apps.forum_conversation.forms import PostForm as AbstractPostForm
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model
from machina.core.loading import get_class


Post = get_model("forum_conversation", "Post")
get_anonymous_user_forum_key = get_class(
    "forum_permission.shortcuts",
    "get_anonymous_user_forum_key",
)


class PostForm(AbstractPostForm):
    subject = CharField(widget=HiddenInput(), max_length=1, required=False)

    def create_post(self):
        post = Post(
            topic=self.topic,
            subject=f"{machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX} {self.topic.subject}",
            approved=self.perm_handler.can_post_without_approval(self.forum, self.user),
            content=self.cleaned_data["content"],
            enable_signature=self.cleaned_data["enable_signature"],
        )
        if not self.user.is_anonymous:
            post.poster = self.user
        else:
            post.username = self.cleaned_data["username"]
            post.anonymous_key = get_anonymous_user_forum_key(self.user)
        return post
