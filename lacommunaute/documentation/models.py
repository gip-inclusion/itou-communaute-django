from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
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

    def get_absolute_url(self, with_fqdn=False):
        absolute_url = reverse("documentation:category_detail", kwargs={"slug": self.slug, "pk": self.pk})
        if with_fqdn:
            return f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{absolute_url}"
        return absolute_url

    def get_update_url(self):
        return reverse("documentation:category_update", kwargs={"pk": self.pk, "slug": self.slug})


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

    def get_absolute_url(self, with_fqdn=False):
        absolute_url = reverse(
            "documentation:document_detail",
            kwargs={
                "category_pk": self.category.pk,
                "slug": self.slug,
                "pk": self.pk,
            },
        )
        if with_fqdn:
            return f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{absolute_url}"
        return absolute_url


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
