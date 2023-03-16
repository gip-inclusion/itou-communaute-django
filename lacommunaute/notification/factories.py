import factory
import factory.django
from faker import Faker

from lacommunaute.notification.models import EmailSentTrack


faker = Faker()


class EmailSentTrackFactory(factory.django.DjangoModelFactory):
    status_code = faker.pyint()
    response = faker.text()
    datas = {"text": faker.text()}

    class Meta:
        model = EmailSentTrack
