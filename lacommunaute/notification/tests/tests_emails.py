import json

import httpx
import respx
from django.test import TestCase
from faker import Faker

from config.settings.base import DEFAULT_FROM_EMAIL, SIB_CONTACTS_URL, SIB_SMTP_URL
from lacommunaute.notification.emails import bulk_send_user_to_list, send_email
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.users.factories import UserFactory


faker = Faker()


class SendEmailTestCase(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))
        respx.post(SIB_CONTACTS_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

    @respx.mock
    def test_send_email(self):
        to = [{"email": faker.email()}]
        params = faker.text()
        template_id = faker.random_int()
        kind = "first_reply"

        payload = {
            "sender": {"name": "La Communauté", "email": DEFAULT_FROM_EMAIL},
            "to": to,
            "params": params,
            "templateId": template_id,
        }

        send_email(to, params, template_id, kind)

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)
        self.assertEqual(email_sent_track.kind, "first_reply")

    @respx.mock
    def test_bulk_send_user_to_list(self):
        users = UserFactory.create_batch(3)
        list_id = faker.random_int()

        payload = {
            "jsonBody": [
                {"email": user.email, "attributes": {"NOM": user.last_name, "PRENOM": user.first_name}}
                for user in users
            ],
            "emailBlacklist": False,
            "smsBlacklist": False,
            "listIds": [list_id],
            "updateExistingContacts": True,
            "emptyContactsAttributes": True,
        }

        bulk_send_user_to_list(users, list_id)

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)
        self.assertEqual(email_sent_track.kind, "onboarding")
