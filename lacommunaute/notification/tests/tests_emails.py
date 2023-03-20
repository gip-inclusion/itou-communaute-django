import json

import httpx
import respx
from django.test import TestCase, override_settings
from faker import Faker

from config.settings.base import DEFAULT_FROM_EMAIL, SIB_CONTACTS_URL, SIB_SMTP_URL
from lacommunaute.notification.emails import add_user_to_list, send_email
from lacommunaute.notification.models import EmailSentTrack


faker = Faker()


@override_settings(
    SIB_CONTACTS_URL="https://sendinblue.contacts.fake",
)
class SendEmailTestCase(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))
        respx.post(SIB_CONTACTS_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

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
        self.assertEqual(email_sent_track.kind, "first_reply")

    @respx.mock
    def test_add_user_to_list(self):
        email = faker.email()
        firstname = faker.first_name()
        lastname = faker.last_name()
        list_id = faker.random_int()

        payload = {
            "email": email,
            "attributes": {
                "FNAME": firstname,
                "LNAME": lastname,
            },
            "emailBlacklisted": False,
            "smsBlacklisted": False,
            "listIds": [list_id],
            "updateEnabled": True,
        }

        add_user_to_list(email, firstname, lastname, list_id)

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)
        self.assertEqual(email_sent_track.kind, "onboarding")
