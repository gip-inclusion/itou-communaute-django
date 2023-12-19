import factory

from lacommunaute.surveys.models import DSP
from lacommunaute.users.factories import UserFactory


class DSPFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DSP

    user = factory.SubFactory(UserFactory)
    recommendations = {
        "Recommandations": "Parcours SIAE",
    }
