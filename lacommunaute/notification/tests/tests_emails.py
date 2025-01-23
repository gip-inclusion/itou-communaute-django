import json

import httpx
import respx
from django.conf import settings
from django.test import TestCase
from faker import Faker

from lacommunaute.notification.emails import SIB_CONTACTS_URL, SIB_SMTP_URL, bulk_send_user_to_list, send_email
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.users.factories import UserFactory


faker = Faker()


class SendEmailTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, text='{"message": "OK"}'))
        cls.to = [{"email": faker.email()}]
        cls.params = faker.text()
        cls.template_id = faker.random_int()
        cls.kind = "first_reply"
        cls.payload = {
            "sender": {"name": "La Communauté", "email": settings.DEFAULT_FROM_EMAIL},
            "to": cls.to,
            "params": cls.params,
            "templateId": cls.template_id,
        }

    @respx.mock
    def test_send_email(self):
        send_email(self.to, self.params, self.template_id, self.kind)

        email_sent_track = EmailSentTrack.objects.get()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, self.payload)
        self.assertEqual(email_sent_track.kind, self.kind)

    @respx.mock
    def test_send_email_with_bcc(self):
        self.payload["bcc"] = [{"email": faker.email()}]

        send_email(self.to, self.params, self.template_id, self.kind, self.payload["bcc"])

        email_sent_track = EmailSentTrack.objects.get()
        self.assertEqual(email_sent_track.datas, self.payload)


class BulkSendUserToListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        respx.post(SIB_CONTACTS_URL).mock(return_value=httpx.Response(200, text='{"message": "OK"}'))

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
