from django.contrib import messages
from django.urls import reverse
from machina.apps.forum_moderation.views import (
    PostDisapproveView as BasePostDisapproveView,
    TopicDeleteView as BaseTopicDeleteView,
)

from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.models import BlockedEmail, BlockedPost


class TopicDeleteView(BaseTopicDeleteView):
    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse("pages:home")


class PostDisapproveView(BasePostDisapproveView):
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if post.username:
            _, created = BlockedEmail.objects.get_or_create(
                email=post.username, defaults={"reason": "Post disapproved"}
            )
            if created:
                messages.warning(
                    self.request, "l'adresse email de l'utilisateur a été ajoutée à la liste des emails bloqués."
                )
            else:
                messages.warning(
                    self.request,
                    "l'adresse email de l'utilisateur est déjà dans la liste des emails bloqués.",
                )
        return self.disapprove(request, *args, **kwargs)

    def disapprove(self, request, *args, **kwargs):
        """
        Extends Machina's post disapproval behaviour to save the rejected post before deleting
        """
        self.object = self.get_object()
        self.object.update_reason = BlockedPostReason.MODERATOR_DISAPPROVAL.value
        BlockedPost.create_from_post(self.object)
        return super().disapprove(request, *args, **kwargs)
