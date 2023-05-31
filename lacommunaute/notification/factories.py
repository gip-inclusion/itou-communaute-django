import factory
import factory.django
from faker import Faker

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import BouncedEmail, EmailSentTrack


faker = Faker()


class EmailSentTrackFactory(factory.django.DjangoModelFactory):
    status_code = faker.pyint()
    response = faker.text()
    datas = {"text": faker.text()}
    kind = EmailSentTrackKind.FIRST_REPLY

    class Meta:
        model = EmailSentTrack


class BouncedEmailFactory(factory.django.DjangoModelFactory):
    email = faker.unique.email()
    reason = factory.Faker("sentence", nb_words=5)

    class Meta:
        model = BouncedEmail
