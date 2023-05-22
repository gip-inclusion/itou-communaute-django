import json

import httpx
import respx
from django.conf import settings
from django.test import TestCase
from faker import Faker

from config.settings.base import (
    DEFAULT_FROM_EMAIL,
    SIB_CONTACT_LIST_URL,
    SIB_CONTACTS_URL,
    SIB_ONBOARDING_LIST,
    SIB_SMTP_URL,
    SIB_UNANSWERED_QUESTION_TEMPLATE,
)
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.notification.tasks import (
    add_user_to_list_when_register,
    send_notifs_on_unanswered_topics,
    send_notifs_when_first_reply,
)
from lacommunaute.users.factories import UserFactory


faker = Faker()


class SendNotifsWhenFirstReplyTestCase(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

    @respx.mock
    def test_send_notifs_when_first_reply(self):
        topic = TopicFactory(with_post=True)
        post = PostFactory(topic=topic)

        url = f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{post.topic.get_absolute_url()}"
        url += "?mtm_campaign=firstreply&mtm_medium=email"

        params = {
            "url": url,
            "topic_subject": topic.subject,
            "display_name": post.poster_display_name,
        }
        payload = {
            "sender": {"name": "La Communauté", "email": DEFAULT_FROM_EMAIL},
            "to": [{"email": topic.poster_email}],
            "params": params,
            "templateId": 2,
        }

        send_notifs_when_first_reply()

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)


class AddUserToListWhenRegister(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_CONTACTS_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

    @respx.mock
    def test_add_user_to_list_when_register(self):
        users = UserFactory.create_batch(3)

        payload = {
            "jsonBody": [
                {"email": user.email, "attributes": {"NOM": user.last_name, "PRENOM": user.first_name}}
                for user in users
            ],
            "emailBlacklist": False,
            "smsBlacklist": False,
            "listIds": [SIB_ONBOARDING_LIST],
            "updateExistingContacts": True,
            "emptyContactsAttributes": True,
        }
        add_user_to_list_when_register()

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)


class SendNotifsOnUnansweredTopics(TestCase):
    def setUp(self):
        super().setUp()
        self.list_id = faker.random_int()
        self.contact_list_response = {
            "contacts": [
                {
                    "email": faker.email(),
                    "emailBlacklisted": False,
                    "attributes": {"PRENOM": faker.first_name(), "NOM": faker.name()},
                },
            ]
        }
        respx.get(SIB_CONTACT_LIST_URL + f"/{self.list_id}/contacts").mock(
            return_value=httpx.Response(200, json=self.contact_list_response)
        )
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

    @respx.mock
    def test_send_notifs_on_unanswered_topics(self):
        TopicFactory(with_post=True, forum=ForumFactory(is_private=False))
        expected_contact = self.contact_list_response["contacts"][0]
        to = [
            {
                "email": expected_contact["email"],
                "name": f'{expected_contact["attributes"]["PRENOM"]} {expected_contact["attributes"]["NOM"]}',
            }
        ]

        url = (
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}/"
            "?new=1&mtm_campaign=unsanswered&mtm_medium=email#community"
        )

        params = {"count": 1, "link": url}
        payload = {
            "sender": {"name": "La Communauté", "email": DEFAULT_FROM_EMAIL},
            "to": to,
            "params": params,
            "templateId": SIB_UNANSWERED_QUESTION_TEMPLATE,
        }

        send_notifs_on_unanswered_topics(self.list_id)

        self.assertEqual(EmailSentTrack.objects.count(), 1)
        email_sent_track = EmailSentTrack.objects.first()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertEqual(email_sent_track.response, json.dumps({"message": "OK"}))
        self.assertEqual(email_sent_track.datas, payload)

    @respx.mock
    def test_send_notifs_on_unanswered_topics_with_no_topic(self):
        send_notifs_on_unanswered_topics(self.list_id)

        self.assertEqual(EmailSentTrack.objects.count(), 0)
