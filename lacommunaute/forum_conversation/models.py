from django.db.models import EmailField
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic


class Topic(AbstractTopic):
    pass


class Post(AbstractPost):
    username = EmailField(blank=True, null=True, verbose_name=("Adresse email"))
