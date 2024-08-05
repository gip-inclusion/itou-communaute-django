import random
from datetime import timedelta

import factory
import factory.django
from django.utils import timezone
from faker import Faker

from lacommunaute.notification.enums import EmailSentTrackKind
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
    recipient = faker.email()
    kind = EmailSentTrackKind.FIRST_REPLY
    post = None

    class Meta:
        model = Notification

    class Params:
        is_sent = factory.Trait(sent_at=(timezone.now() - timedelta(days=random.randint(0, 90))))
