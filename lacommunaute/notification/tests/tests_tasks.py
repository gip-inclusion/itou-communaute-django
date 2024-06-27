import json

import httpx
import respx
from django.conf import settings
from django.template.defaultfilters import pluralize
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from config.settings.base import (
    DEFAULT_FROM_EMAIL,
    NEW_MESSAGES_EMAIL_MAX_PREVIEW,
    SIB_CONTACT_LIST_URL,
    SIB_CONTACTS_URL,
    SIB_NEW_MESSAGES_TEMPLATE,
    SIB_ONBOARDING_LIST,
    SIB_SMTP_URL,
    SIB_UNANSWERED_QUESTION_TEMPLATE,
)
from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.notification.models import EmailSentTrack, Notification
from lacommunaute.notification.tasks import (
    add_user_to_list_when_register,
    send_messages_notifications,
    send_notifs_on_unanswered_topics,
)
from lacommunaute.notification.utils import get_serialized_messages
from lacommunaute.users.factories import UserFactory


faker = Faker()


class SendMessageNotificationsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))

    def get_expected_email_payload(self, notifications):
        grouped_notifications = notifications.select_related(
            "post", "post__topic", "post__poster"
        ).group_by_recipient()

        assert (
            len(grouped_notifications.keys()) == 1
        ), "get_expected_email_payload requires notifications with only one recipient"

        recipient = list(grouped_notifications.keys())[0]
        recipient_notifications = grouped_notifications[recipient]
        message_count = len(recipient_notifications)
        message_count_text = f"{message_count} message{pluralize(message_count, 's')}"

        params = {
            "email_object": "Bonne nouvelle, ça bouge pour vous dans la communauté !",
            "email_thumbnail": (f"Vous avez {message_count_text} à découvrir sur la communauté de l'inclusion"),
            "messages": get_serialized_messages(recipient_notifications[:NEW_MESSAGES_EMAIL_MAX_PREVIEW]),
        }

        return {
            "to": [{"email": DEFAULT_FROM_EMAIL}],
            "bcc": [{"email": recipient}],
            "params": params,
            "sender": {"name": "La Communauté", "email": DEFAULT_FROM_EMAIL},
            "templateId": SIB_NEW_MESSAGES_TEMPLATE,
        }

    @respx.mock
    def test_send_messages_notifications_asap(self):
        topic = TopicFactory(with_post=True)
        notification = NotificationFactory(post=topic.first_post, delay=NotificationDelay.ASAP)

        send_messages_notifications(NotificationDelay.ASAP)

        email_sent_track = EmailSentTrack.objects.get()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertJSONEqual(email_sent_track.response, {"message": "OK"})
        self.assertEqual(
            email_sent_track.datas, self.get_expected_email_payload(Notification.objects.filter(id=notification.id))
        )

    @respx.mock
    def test_send_messages_notifications_day(self):
        topic = TopicFactory(with_post=True)
        notification = NotificationFactory(post=topic.first_post, delay=NotificationDelay.DAY)

        send_messages_notifications(NotificationDelay.DAY)

        email_sent_track = EmailSentTrack.objects.get()
        self.assertEqual(email_sent_track.status_code, 200)
        self.assertJSONEqual(email_sent_track.response, {"message": "OK"})
        self.assertEqual(
            email_sent_track.datas, self.get_expected_email_payload(Notification.objects.filter(id=notification.id))
        )

    @respx.mock
    def test_send_messages_notifications_max_messages_preview(self):
        topic = TopicFactory(with_post=True)
        notif_count_to_generate = NEW_MESSAGES_EMAIL_MAX_PREVIEW + 1

        NotificationFactory.create_batch(
            notif_count_to_generate,
            recipient="test@example.com",
            delay=NotificationDelay.ASAP,
            kind=EmailSentTrackKind.FIRST_REPLY,
            post=topic.first_post,
        )

        send_messages_notifications(NotificationDelay.ASAP)

        email_sent_track = EmailSentTrack.objects.get()
        self.assertEqual(len(email_sent_track.datas["params"]["messages"]), NEW_MESSAGES_EMAIL_MAX_PREVIEW)
        self.assertEqual(
            email_sent_track.datas["params"]["email_thumbnail"],
            (f"Vous avez {notif_count_to_generate } messages à découvrir sur la communauté de l'inclusion"),
        )

    @respx.mock
    def test_send_messages_notifications_num_queries(self):
        expected_queries = 1

        NotificationFactory(delay=NotificationDelay.ASAP)

        with self.assertNumQueries(expected_queries):
            send_messages_notifications(NotificationDelay.ASAP)

        NotificationFactory.create_batch(10, delay=NotificationDelay.ASAP)

        with self.assertNumQueries(expected_queries):
            send_messages_notifications(NotificationDelay.ASAP)


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

    def test_no_user_to_add(self):
        add_user_to_list_when_register()

        self.assertEqual(EmailSentTrack.objects.count(), 0)


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
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PUBLIC_FORUM))
        expected_contact = self.contact_list_response["contacts"][0]
        to = [
            {
                "email": expected_contact["email"],
                "name": f'{expected_contact["attributes"]["PRENOM"]} {expected_contact["attributes"]["NOM"]}',
            }
        ]

        url = (
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}",
            reverse("forum_conversation_extension:topics"),
            "?filter=NEW&mtm_campaign=unsanswered&mtm_medium=email#community",
        )

        params = {"count": 1, "link": "".join(url)}
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
