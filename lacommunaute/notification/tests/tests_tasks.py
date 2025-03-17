import json

import httpx
import pytest
import respx
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from faker import Faker

from lacommunaute.forum_conversation.factories import (
    TopicFactory,
)
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.notification.emails import SIB_CONTACTS_URL, SIB_SMTP_URL
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.notification.tasks import (
    add_user_to_list_when_register,
    send_messages_notifications,
    send_missyou_notifications,
    send_notifs_on_unanswered_topics,
)
from lacommunaute.notification.utils import get_serialized_messages
from lacommunaute.users.factories import UserFactory


faker = Faker()


@pytest.fixture(name="mock_respx_post_to_sib_smtp_url")
def mock_respx_post_to_sib_smtp_url_fixture():
    with respx.mock:
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, text='{"message": "OK"}'))
        yield


def check_generic_payload(email, templateId, payload):
    return (
        payload["to"] == [{"email": email}]
        and payload["sender"] == {"name": "La Communauté", "email": settings.DEFAULT_FROM_EMAIL}
        and payload["templateId"] == templateId
    )


class TestSendMessagesNotifications:
    def test_grouped_asap_notifications(self, db, mock_respx_post_to_sib_smtp_url):
        user = UserFactory()
        notifications = [
            NotificationFactory(recipient=user.email, delay=NotificationDelay.ASAP, set_post=True),
            NotificationFactory(recipient=user.email, delay=NotificationDelay.ASAP, set_anonymous_post=True),
        ]
        NotificationFactory(recipient=user.email, set_post=True)

        send_messages_notifications(NotificationDelay.ASAP)
        email_sent_track = EmailSentTrack.objects.get()

        assert check_generic_payload(user.email, settings.SIB_NEW_MESSAGES_TEMPLATE, email_sent_track.datas)

        for attr, expected in [
            ("messages", get_serialized_messages(notifications)),
            ("email_thumbnail", "Vous avez 2 messages à découvrir sur la communauté de l'inclusion"),
        ]:
            assert email_sent_track.datas["params"][attr] == expected

    def test_grouped_day_notifications(self, db, mock_respx_post_to_sib_smtp_url):
        user = UserFactory()
        notifications = [
            NotificationFactory(recipient=user.email, set_post=True),
            NotificationFactory(recipient=user.email, set_anonymous_post=True),
        ]
        NotificationFactory(recipient=user.email, delay=NotificationDelay.ASAP, set_post=True)

        send_messages_notifications(NotificationDelay.DAY)
        email_sent_track = EmailSentTrack.objects.get()

        assert check_generic_payload(user.email, settings.SIB_NEW_MESSAGES_TEMPLATE, email_sent_track.datas)

        for attr, expected in [
            ("messages", get_serialized_messages(notifications)),
            ("email_thumbnail", "Vous avez 2 messages à découvrir sur la communauté de l'inclusion"),
        ]:
            assert email_sent_track.datas["params"][attr] == expected

    def test_grouped_max_messages_preview(self, db, mock_respx_post_to_sib_smtp_url):
        NotificationFactory.create_batch(
            settings.NEW_MESSAGES_EMAIL_MAX_PREVIEW + 1, recipient=UserFactory().email, set_post=True
        )

        send_messages_notifications(NotificationDelay.DAY)
        email_sent_track = EmailSentTrack.objects.get()

        assert len(email_sent_track.datas["params"]["messages"]) == settings.NEW_MESSAGES_EMAIL_MAX_PREVIEW
        assert (
            email_sent_track.datas["params"]["email_thumbnail"]
            == "Vous avez 11 messages à découvrir sur la communauté de l'inclusion"
        )

    def test_num_queries(self, db, django_assert_num_queries, mock_respx_post_to_sib_smtp_url):
        NotificationFactory.create_batch(
            10,
            recipient=UserFactory().email,
            set_post=True,
        )

        with django_assert_num_queries(3):
            send_messages_notifications(NotificationDelay.DAY)


class TestSendMissyouNotifications:
    def test_send_missyou_notifications(self, db, mock_respx_post_to_sib_smtp_url):
        user = UserFactory()
        notification = NotificationFactory(
            recipient=user.email,
            delay=NotificationDelay.ASAP,
            kind=EmailSentTrackKind.MISSYOU,
        )

        send_missyou_notifications(NotificationDelay.ASAP)
        email_sent_track = EmailSentTrack.objects.get()

        assert check_generic_payload(user.email, settings.SIB_MISSYOU_TEMPLATE, email_sent_track.datas)
        assert (
            email_sent_track.datas["params"]["url"]
            == f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{reverse('pages:home')}?notif={notification.uuid}"
        )
        assert email_sent_track.datas["params"]["email_thumbnail"] == (
            "Nous espérons que vous allez bien ! Ca fait longtemps "
            "qu’on ne vous a pas vu dans la communauté de l’inclusion"
        )

    @pytest.mark.parametrize("delay", [NotificationDelay.DAY, NotificationDelay.ASAP])
    def test_missyou_notifications_ignores_messages_notifications(self, db, delay, mock_respx_post_to_sib_smtp_url):
        user = UserFactory()
        (NotificationFactory(recipient=user.email, delay=delay, set_post=True),)
        (NotificationFactory(recipient=user.email, delay=delay, set_anonymous_post=True),)

        send_missyou_notifications(delay)
        assert EmailSentTrack.objects.count() == 0


class AddUserToListWhenRegister(TestCase):
    def setUp(self):
        super().setUp()
        respx.post(SIB_CONTACTS_URL).mock(return_value=httpx.Response(200, text='{"message": "OK"}'))

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
            "listIds": [settings.SIB_ONBOARDING_LIST],
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
        "sender": {"name": "La Communauté", "email": settings.DEFAULT_FROM_EMAIL},
        "to": to,
        "params": params,
        "templateId": settings.SIB_UNANSWERED_QUESTION_TEMPLATE,
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

    @pytest.mark.parametrize(
        "data", [lambda: UserFactory(is_in_staff_group=True), lambda: TopicFactory(with_post=True)]
    )
    def test_send_notifs_on_unanswered_topics_with_no_topic(self, db, data, mock_respx_post_to_sib_smtp_url):
        data = data()
        send_notifs_on_unanswered_topics()
        assert EmailSentTrack.objects.count() == 0
