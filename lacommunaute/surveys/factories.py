import factory
from dateutil.relativedelta import relativedelta

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
    location = factory.Faker("city")
    city_code = factory.Faker("postcode")

    class Params:
        for_snapshot_level_min = factory.Trait(
            work_capacity=0,
            language_skills=0,
            housing=0,
            rights_access=0,
            mobility=0,
            resources=0,
            judicial=0,
            availability=0,
            location="Caen",
            city_code="14000",
        )
        for_snapshot_level_1 = factory.Trait(
            work_capacity=1,
            language_skills=1,
            housing=1,
            rights_access=1,
            mobility=1,
            resources=1,
            judicial=1,
            availability=1,
            location="Nancy",
            city_code="54000",
        )
        for_snapshot_level_2 = factory.Trait(
            work_capacity=2,
            language_skills=2,
            housing=2,
            rights_access=2,
            mobility=2,
            resources=2,
            judicial=2,
            availability=2,
            location="Nantes",
            city_code="44000",
        )
        for_snapshot_level_max = factory.Trait(
            work_capacity=3,
            language_skills=3,
            housing=3,
            rights_access=3,
            mobility=3,
            resources=3,
            judicial=2,  # 2 is the max value for judicial
            availability=3,
            location="Rouen",
            city_code="76000",
        )

    @factory.post_generation
    def recommendations(obj, create, extracted, **kwargs):
        if create and isinstance(extracted, int):
            obj.recommendations.set(get_recommendations(obj))

    @factory.post_generation
    def months_ago(obj, create, extracted, **kwargs):
        if create and isinstance(extracted, int):
            obj.created = obj.created - relativedelta(months=extracted)
            obj.save()
