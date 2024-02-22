from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from machina.apps.forum_member.abstract_models import AbstractForumProfile

from lacommunaute.forum_member.enums import ActiveSearch, Regions
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


class ForumProfileQuerySet(models.QuerySet):
    def power_users(self):
        return (
            self.filter(user__posts__created__gte=timezone.now() - relativedelta(days=30))
            .annotate(user_posts_count=models.Count("user__posts"))
            .filter(user_posts_count__gte=3)
            .order_by("-user_posts_count")
            .select_related("user")
            .prefetch_related("user__posts")
        )


class ForumProfile(AbstractForumProfile):
    linkedin = models.URLField(blank=True, null=True, verbose_name="lien vers votre profil LinkedIn")
    cv = models.FileField(upload_to="cv/", blank=True, null=True, verbose_name="votre CV")
    search = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=ActiveSearch.choices,
        default=ActiveSearch.NO,
        verbose_name="recherche active",
    )
    region = models.CharField(
        max_length=100, blank=True, null=True, choices=Regions.choices, default=Regions.RXX, verbose_name="région"
    )
    internship_duration = models.IntegerField(default=0, verbose_name="durée du stage (en mois)")
    updated_at = models.DateTimeField(auto_now=True)

    objects = ForumProfileQuerySet().as_manager()

    def __str__(self):
        return get_forum_member_display_name(self.user)
