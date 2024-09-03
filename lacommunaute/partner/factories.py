import factory
from faker import Faker

from lacommunaute.partner.models import Partner


faker = Faker()


class PartnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Partner

    name = factory.LazyAttribute(lambda x: faker.company())
    short_description = factory.LazyAttribute(lambda x: faker.text(max_nb_chars=200))
    description = factory.LazyAttribute(
        lambda x: "\n".join([f"### part {i} \n{faker.paragraph(nb_sentences=20)}" for i in range(2)])
    )
    url = factory.LazyAttribute(lambda x: faker.url())

    class Params:
        with_logo = factory.Trait(logo=factory.django.ImageField(filename="test.jpg"))
        for_snapshot = factory.Trait(
            name="Best Partner Ever",
            description="### h3 long MD description \n lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            short_description="short description for SEO",
            url="https://www.best-partner-ever.com",
        )
