import random
from datetime import timedelta

import factory
import factory.django
from django.utils import timezone
from faker import Faker

from lacommunaute.forum_conversation.factories import AnonymousPostFactory, TopicFactory
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.models import EmailSentTrack, Notification


faker = Faker()


class EmailSentTrackFactory(factory.django.DjangoModelFactory):
    status_code = faker.pyint()
    response = faker.text()
    datas = {"text": faker.text()}
    kind = EmailSentTrackKind.FIRST_REPLY

    class Meta:
        model = EmailSentTrack


class NotificationFactory(factory.django.DjangoModelFactory):
    recipient = factory.Faker("email")
    kind = EmailSentTrackKind.FIRST_REPLY
    delay = NotificationDelay.DAY

    class Meta:
        model = Notification
        skip_postgeneration_save = True

    class Params:
        is_sent = factory.Trait(sent_at=(timezone.now() - timedelta(days=random.randint(0, 90))))
        set_post = factory.Trait(post=factory.LazyAttribute(lambda o: TopicFactory(with_post=True).first_post))
        set_anonymous_post = factory.Trait(
            post=factory.LazyAttribute(lambda o: AnonymousPostFactory(topic=TopicFactory()))
        )
