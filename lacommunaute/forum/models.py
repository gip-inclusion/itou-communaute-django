import uuid

from django.contrib.auth.models import Group
from django.db import models
from machina.apps.forum.abstract_models import AbstractForum


class Forum(AbstractForum):
    members_group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE, verbose_name=("Members Group"))
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
