import factory
import factory.django
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
    kind = EmailSentTrackKind.NEW_MESSAGES
    post = None

    class Meta:
        model = Notification

    class Params:
        is_sent = factory.Trait(sent_at=faker.past_datetime())
