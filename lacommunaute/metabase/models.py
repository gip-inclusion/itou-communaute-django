from django.db import models

from lacommunaute.forum.enums import Kind as Forum_Kind


class ForumTable(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    kind = models.CharField(
        max_length=20, choices=Forum_Kind.choices, default=Forum_Kind.PUBLIC_FORUM, verbose_name="Kind"
    )
    type = models.CharField(max_length=20, verbose_name="Type")
    short_description_boolean = models.BooleanField(default=False, verbose_name="Présence d'une description courte")
    description_boolean = models.BooleanField(default=False, verbose_name="Présence d'une description")
    parent_name = models.CharField(null=True, max_length=100, verbose_name="Nom du forum parent")
    direct_topics_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de sujets directs")
    upvotes_count = models.PositiveIntegerField(default=0, verbose_name="Nombre d'upvotes")
    last_post_at = models.DateTimeField(null=True, verbose_name="Date du dernier message")
    last_updated_at = models.DateTimeField(null=True, verbose_name="Date de dernière mise à jour")
    extracted_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'extraction des données")

    objects = models.Manager()

    class Meta:
        verbose_name = "Forum Table"
        verbose_name_plural = "Forums Table"
        ordering = ["name"]

    def __str__(self):
        return self.name
