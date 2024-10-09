from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from lacommunaute.utils.abstract_models import Publication


class Partner(Publication):
    url = models.URLField(verbose_name="Lien vers le site du partenaire", null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")
        ordering = ["-updated"]

    def get_absolute_url(self):
        return reverse("partner:detail", kwargs={"slug": self.slug, "pk": self.pk})
