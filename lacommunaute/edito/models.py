from django.conf import settings
from django.db import models
from machina.models.abstract_models import DatedModel
from machina.models.fields import MarkupTextField


class Edito(DatedModel):
    title = models.CharField(max_length=100, verbose_name="title")
    content = MarkupTextField(verbose_name="Contenu", null=True, blank=True)
    url = models.URLField(verbose_name="URL du lien", null=True, blank=True)
    link_title = models.CharField(max_length=100, verbose_name="Titre du lien")

    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Poster",
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Edito"
        verbose_name_plural = "Editos"
        ordering = ["-updated"]

    def __str__(self):
        return f"{self.title}"
