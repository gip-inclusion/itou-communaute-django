from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from machina.models.abstract_models import DatedModel


class BlockedEmail(DatedModel):
    email = models.EmailField(verbose_name="email", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "email bloqué"
        verbose_name_plural = "emails bloqués"

    def __str__(self):
        return f"{self.email} - {self.created}"


class BlockedDomainName(DatedModel):
    domain = models.CharField(max_length=253, verbose_name="domaine", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "nom de domaine bloqué"
        verbose_name_plural = "nom de domaines bloqués"

    def __str__(self):
        return f"{self.domain} - {self.created}"


class BlockedPost(DatedModel):
    """
    When a user submits a Post and it is blocked by our quality control app (forum_moderation),
    we save a record of the blocked Post in this table for reference purposes

    It is built of a subset of fields from django-machina's model AbstractPost
    """

    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="blocked_posts",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name=_("Poster"),
    )
    username = models.EmailField(blank=True, null=True, verbose_name=("Adresse email"))
    content = models.CharField(verbose_name=_("Content"))
    block_reason = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Block Reason"),
    )

    class Meta:
        verbose_name = _("Blocked Post")
        verbose_name_plural = _("Blocked Posts")

    def __str__(self):
        return f"Blocked Message [{ str(self.created) }]"

    @classmethod
    def create_from_post(cls, post):
        """
        Creates a BlockedPost object from parameterised Post (machina)
        """
        return cls.objects.create(
            poster=post.poster,
            username=getattr(post, "username", ""),
            content=str(post.content),
            block_reason=post.update_reason,
        )
