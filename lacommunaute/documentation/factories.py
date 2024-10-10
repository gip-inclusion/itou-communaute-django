import factory
from faker import Faker

from lacommunaute.documentation.models import Category, Document, DocumentRating


faker = Faker()


class AbstractDocumentationFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=100)
    short_description = factory.Faker("sentence", nb_words=10)
    image = factory.django.ImageField(filename="banner.jpg")


class CategoryFactory(AbstractDocumentationFactory):
    class Meta:
        model = Category

    class Params:
        for_snapshot = factory.Trait(
            name="Test Category", description="Test description", short_description="Test short description"
        )


class DocumentFactory(AbstractDocumentationFactory):
    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = Document

    class Params:
        for_snapshot = factory.Trait(
            name="Test Document",
            description="Test description",
            short_description="Test short description",
            category=factory.SubFactory(CategoryFactory, for_snapshot=True),
        )

    @factory.post_generation
    def with_tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        if isinstance(extracted, list):
            for tag in extracted:
                self.tags.add(tag)


class DocumentRatingFactory(factory.django.DjangoModelFactory):
    document = factory.SubFactory(DocumentFactory)
    rating = factory.Faker("random_int", min=1, max=5)

    class Meta:
        model = DocumentRating
        skip_postgeneration_save = True

    @factory.post_generation
    def set_created(self, create, extracted, **kwargs):
        if extracted:
            self.created = extracted
            self.save()
