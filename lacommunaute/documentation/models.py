from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.partner.models import Partner
from lacommunaute.utils.abstract_models import Publication


class Category(Publication):
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["created"]

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("documentation:category_detail", kwargs={"pk": self.pk, "slug": self.slug})


class Document(Publication):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="documents")
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True)
    upvotes = GenericRelation(UpVote, related_query_name="document")
    certified = models.BooleanField(default=False, verbose_name="Certifié par la communauté de l'inclusion")
    tags = TaggableManager()

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name}"
