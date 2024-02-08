from django.contrib import messages
from django.urls import reverse
from machina.apps.forum_moderation.views import (
    PostDisapproveView as BasePostDisapproveView,
    TopicDeleteView as BaseTopicDeleteView,
)

from lacommunaute.notification.models import BouncedEmail


class TopicDeleteView(BaseTopicDeleteView):
    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse("pages:home")


class PostDisapproveView(BasePostDisapproveView):
    def post(self, request, *args, **kwargs):
        post = self.get_object()
        if post.username:
            if BouncedEmail.objects.filter(email=post.username).exists():
                messages.warning(
                    self.request,
                    "l'adresse email de l'utilisateur est déjà dans la liste des emails bloqués.",
                )
            else:
                BouncedEmail.objects.create(email=post.username, reason="Post disapproved")
                messages.warning(
                    self.request, "l'adresse email de l'utilisateur a été ajoutée à la liste des emails bloqués."
                )
        return self.disapprove(request, *args, **kwargs)
