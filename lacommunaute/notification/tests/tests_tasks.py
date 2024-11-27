import json

import httpx
import pytest
import respx
from django.conf import settings
from django.template.defaultfilters import pluralize
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from config.settings.base import (
    DEFAULT_FROM_EMAIL,
    NEW_MESSAGES_EMAIL_MAX_PREVIEW,
    SIB_CONTACTS_URL,
    SIB_NEW_MESSAGES_TEMPLATE,
    SIB_ONBOARDING_LIST,
    SIB_SMTP_URL,
    SIB_UNANSWERED_QUESTION_TEMPLATE,
)
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
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

        self.assertIsNone(Notification.objects.filter(sent_at__isnull=True).first())
        self.assertEqual(Notification.objects.all().values("sent_at").distinct().count(), 1)

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

        self.assertIsNone(Notification.objects.filter(sent_at__isnull=True).first())
        self.assertEqual(Notification.objects.all().values("sent_at").distinct().count(), 1)

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
        expected_queries = 2

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


@pytest.fixture(name="mock_respx_post_to_sib_smtp_url")
def mock_respx_post_to_sib_smtp_url_fixture():
    with respx.mock:
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))
        yield


@pytest.fixture(name="payload_for_staff_user_to_notify_on_unanswered_topics")
def payload_for_staff_user_to_notify_on_unanswered_topics_fixture():
    staff_user = UserFactory(is_staff=True, for_snapshot=True)
    TopicFactory(with_post=True)
    to = [
        {
            "email": staff_user.email,
            "name": get_forum_member_display_name(staff_user),
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
    yield payload


class TestSendNotifsOnUnansweredTopics:
    def test_send_notifs_on_unanswered_topics(
        self, db, payload_for_staff_user_to_notify_on_unanswered_topics, mock_respx_post_to_sib_smtp_url
    ):
        send_notifs_on_unanswered_topics()

        assert EmailSentTrack.objects.count() == 1
        email_sent_track = EmailSentTrack.objects.first()
        assert email_sent_track.status_code == 200
        assert email_sent_track.response == json.dumps({"message": "OK"})
        assert email_sent_track.datas == payload_for_staff_user_to_notify_on_unanswered_topics

    @pytest.mark.parametrize("data", [lambda: UserFactory(is_staff=True), lambda: TopicFactory(with_post=True)])
    def test_send_notifs_on_unanswered_topics_with_no_topic(self, db, data, mock_respx_post_to_sib_smtp_url):
        data = data()
        send_notifs_on_unanswered_topics()
        assert EmailSentTrack.objects.count() == 0
