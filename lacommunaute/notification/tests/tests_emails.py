import json

import httpx
import respx
from django.test import TestCase
from faker import Faker

from config.settings.base import DEFAULT_FROM_EMAIL, SIB_CONTACT_LIST_URL, SIB_CONTACTS_URL, SIB_SMTP_URL
from lacommunaute.notification.emails import bulk_send_user_to_list, collect_users_from_list, send_email
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.users.factories import UserFactory


faker = Faker()


class SendEmailTestCase(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))
        respx.post(SIB_CONTACTS_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

        self.contact_list_response = {
            "contacts": [
                {
                    "email": faker.email(),
                    "emailBlacklisted": False,
                    "attributes": {"PRENOM": faker.first_name(), "NOM": faker.name()},
                },
                {
                    "email": faker.email(),
                    "emailBlacklisted": True,
                    "attributes": {"PRENOM": faker.first_name(), "NOM": faker.name()},
                },
            ]
        }
        respx.get(SIB_CONTACT_LIST_URL + "/1/contacts").mock(
            return_value=httpx.Response(200, json=self.contact_list_response)
        )

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

    def test_collect_users_from_list_bad_status_code(self):
        self.assertIsNone(collect_users_from_list(faker.random_int()))

    @respx.mock
    def test_collect_users_from_list(self):
        expected_contact = self.contact_list_response["contacts"][0]
        contacts = collect_users_from_list(1)
        self.assertEqual(
            contacts,
            [
                {
                    "email": expected_contact["email"],
                    "name": f'{expected_contact["attributes"]["PRENOM"]} {expected_contact["attributes"]["NOM"]}',
                }
            ],
        )
