import factory

from lacommunaute.surveys.models import DSP
from lacommunaute.surveys.recommendations import get_recommendations
from lacommunaute.users.factories import UserFactory


class DSPFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DSP

    user = factory.SubFactory(UserFactory)
    work_capacity = factory.Faker("pyint", min_value=0, max_value=3)
    language_skills = factory.Faker("pyint", min_value=0, max_value=3)
    housing = factory.Faker("pyint", min_value=0, max_value=3)
    rights_access = factory.Faker("pyint", min_value=0, max_value=3)
    mobility = factory.Faker("pyint", min_value=0, max_value=3)
    resources = factory.Faker("pyint", min_value=0, max_value=3)
    judicial = factory.Faker("pyint", min_value=0, max_value=2)
    availability = factory.Faker("pyint", min_value=0, max_value=3)

    @factory.post_generation
    def recommendations(obj, create, extracted, **kwargs):
        if create and isinstance(extracted, int):
            obj.recommendations.set(get_recommendations(obj))
