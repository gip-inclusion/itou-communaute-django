import factory
from machina.test.factories.forum import ForumFactory as BaseForumFactory

from lacommunaute.forum.models import Forum, ForumRating
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import GroupFactory
from lacommunaute.utils.perms import add_public_perms_on_forum


class ForumFactory(BaseForumFactory):
    type = Forum.FORUM_POST
    members_group = factory.SubFactory(GroupFactory, name=factory.SelfAttribute("..name"))
    name = factory.Sequence(lambda n: f"Forum {n}")
    description = factory.Faker("sentence", nb_words=100)
    short_description = factory.Faker("sentence", nb_words=10)

    class Meta:
        skip_postgeneration_save = True

    class Params:
        with_image = factory.Trait(image=factory.django.ImageField(filename="banner.jpg"))

    @factory.post_generation
    def with_public_perms(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        add_public_perms_on_forum(self)

    @factory.post_generation
    def upvoted_by(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for user in extracted:
            UpVote.objects.create(voter=user, content_object=self)


class CategoryForumFactory(ForumFactory):
    type = Forum.FORUM_CAT
    name = factory.Sequence(lambda n: f"Theme {n}")

    @factory.post_generation
    def with_child(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        ForumFactory(parent=self, with_public_perms=True, with_image=True, name=f"{self.name} - Forum")


class ForumRatingFactory(factory.django.DjangoModelFactory):
    forum = factory.SubFactory(ForumFactory)
    rating = factory.Faker("random_int", min=1, max=5)

    class Meta:
        model = ForumRating

    @factory.post_generation
    def set_created(self, create, extracted, **kwargs):
        if extracted:
            self.created = extracted
            self.save()
