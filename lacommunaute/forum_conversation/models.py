from django.db.models import EmailField
from django.urls import reverse
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic


class Topic(AbstractTopic):
    def get_absolute_url(self):
        return reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.pk,
                "slug": self.slug,
            },
        )


class Post(AbstractPost):
    username = EmailField(blank=True, null=True, verbose_name=("Adresse email"))
