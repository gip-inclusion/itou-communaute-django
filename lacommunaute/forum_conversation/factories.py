import factory
from machina.core.db.models import get_model
from machina.test.factories.conversation import PostFactory as BasePostFactory, TopicFactory as BaseTopicFactory


Topic = get_model("forum_conversation", "Topic")


class TopicFactory(BaseTopicFactory):
    subject = factory.Faker("sentence", nb_words=5)
    type = Topic.TOPIC_POST


class PostFactory(BasePostFactory):
    subject = factory.Faker("sentence", nb_words=5)
    content = factory.Faker("sentence", nb_words=40)
