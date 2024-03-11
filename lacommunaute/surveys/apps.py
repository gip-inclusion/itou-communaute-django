from pathlib import Path

import tomllib
from django.apps import AppConfig
from django.db import models


class ForumStatsAppConfig(AppConfig):
    label = "surveys"
    name = "lacommunaute.surveys"
    verbose_name = "Survey"
    verbose_name_plural = "Surveys"

    def ready(self):
        super().ready()
        models.signals.post_migrate.connect(create_update_recommendations, sender=self)


def create_update_recommendations(*args, **kwargs):
    from lacommunaute.surveys.models import Recommendation

    recommendations_specfile = Path(__file__).parent / "recommendations.toml"
    with open(recommendations_specfile, "rb") as f:
        recommendation_specs = tomllib.load(f)
    recommendations = []
    codenames = []
    for spec in recommendation_specs["recommendations"]:
        codename = spec["codename"]
        codenames.append(codename)
        recommendations.append(
            Recommendation(
                codename=codename,
                category=spec["category"],
                text=spec["text"],
            )
        )
    Recommendation.objects.bulk_create(
        recommendations,
        update_conflicts=True,
        unique_fields=("codename",),
        update_fields=("category", "text"),
    )
    Recommendation.objects.exclude(codename__in=codenames).delete()
