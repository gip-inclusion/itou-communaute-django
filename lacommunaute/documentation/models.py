from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from taggit.managers import TaggableManager

from lacommunaute.documentation.abstract_models import AbstractPublication
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.partner.models import Partner


class Category(AbstractPublication):
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.name}"


class Document(AbstractPublication):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="documents")
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True)
    upvotes = GenericRelation(UpVote, related_query_name="document")
    certified = models.BooleanField(default=False, verbose_name="Certifié par la communauté de l'inclusion")
    tags = TaggableManager()

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}"


# use AbstractDatedModel after ForumRanting migration
class DocumentRating(models.Model):
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=40)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Notation d'un document"
        verbose_name_plural = "Notations des documents"
        ordering = ("-created_at",)