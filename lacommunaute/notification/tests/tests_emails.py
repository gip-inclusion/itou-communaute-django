import json

import httpx
import respx
from django.test import TestCase
from faker import Faker

from config.settings.base import DEFAULT_FROM_EMAIL, SIB_URL
from lacommunaute.notification.emails import send_email
from lacommunaute.notification.models import EmailSentTrack


faker = Faker()


class SendEmailTestCase(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

    @respx.mock
    def test_send_email(self):
        to = faker.email()
        params = faker.text()
        template_id = faker.random_int()

        payload = {
            "sender": {"name": "La Communauté", "email": DEFAULT_FROM_EMAIL},
            "to": [{"email": to}],
            "params": params,
            "templateId": template_id,
        }

        send_email(to, params, template_id)

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)
