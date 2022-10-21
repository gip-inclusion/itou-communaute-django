from django.db.models import F
from machina.apps.forum_conversation.forms import PostForm as AbstractPostForm


class PostForm(AbstractPostForm):

    def update_post(self, post):
        if self.user.is_anonymous:
            post.username = self.cleaned_data["username"]
        else:
            post.updated_by = self.user
        post.updates_count = F("updates_count") + 1
