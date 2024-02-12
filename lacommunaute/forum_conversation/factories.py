import factory
from django.conf import settings
from faker import Faker
from machina.test.factories.conversation import PostFactory as BasePostFactory, TopicFactory as BaseTopicFactory

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.forum_polls.factories import TopicPollVoteFactory
from lacommunaute.forum_conversation.models import CertifiedPost, Topic
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import UserFactory


faker = Faker(settings.LANGUAGE_CODE)


class PostFactory(BasePostFactory):
    subject = factory.Faker("sentence", nb_words=5)
    content = factory.Faker("paragraph", nb_sentences=5, locale=settings.LANGUAGE_CODE)
    poster = factory.SubFactory(UserFactory)

    class Meta:
        skip_postgeneration_save = True

    @factory.post_generation
    def upvoted_by(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for user in extracted:
            UpVote.objects.create(voter=user, content_object=self)


class AnonymousPostFactory(PostFactory):
    username = factory.Faker("email")
    poster = None
    anonymous_key = factory.Faker("uuid4")


class CertifiedPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CertifiedPost


class TopicFactory(BaseTopicFactory):
    forum = factory.SubFactory(ForumFactory)
    poster = factory.SubFactory(UserFactory)
    subject = factory.Faker("sentence", nb_words=5)
    type = Topic.TOPIC_POST

    class Meta:
        skip_postgeneration_save = True

    class Params:
        with_post = factory.Trait(
            post=factory.RelatedFactory(
                PostFactory,
                factory_related_name="topic",
                poster=factory.SelfAttribute("topic.poster"),
            )
        )

    @factory.post_generation
    def with_poll_vote(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        TopicPollVoteFactory(poll_option__poll__topic=self, voter=self.poster)

    @factory.post_generation
    def with_certified_post(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        PostFactory(topic=self, poster=self.poster)
        CertifiedPostFactory(topic=self, post=PostFactory(topic=self, poster=self.poster), user=self.poster)

    @factory.post_generation
    def with_tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        if isinstance(extracted, list):
            for tag in extracted:
                self.tags.add(tag)


class AnonymousTopicFactory(TopicFactory):
    poster = None

    class Meta:
        skip_postgeneration_save = True

    class Params:
        with_post = factory.Trait(
            post=factory.RelatedFactory(
                AnonymousPostFactory,
                factory_related_name="topic",
            )
        )
