from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from lacommunaute.event.factories import EventFactory
from lacommunaute.forum.factories import ForumFactory, ForumRatingFactory
from lacommunaute.forum_conversation.factories import AnonymousPostFactory, AnonymousTopicFactory, TopicFactory
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.notification.models import Notification
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import EmailLastSeenFactory, UserFactory
from lacommunaute.users.management.commands.populate_emaillastseen import (
    collect_clicked_notifs,
    collect_DSP,
    collect_event,
    collect_existing_email_last_seen,
    collect_forum_rating,
    collect_post,
    collect_upvote,
    collect_users_logged_in,
    insert_last_seen,
    iterate_over_emails,
    keep_most_recent_tuple,
)
from lacommunaute.users.models import EmailLastSeen


class TestPopulateEmailLastSeen:
    def test_collect_users_logged_in(self, db):
        logged_user = UserFactory(last_login=timezone.make_aware(datetime(2024, 10, 22)))
        UserFactory(last_login=None)
        assert collect_users_logged_in() == ((logged_user.email, logged_user.last_login, EmailLastSeenKind.LOGGED),)

    def test_collect_event(self, db):
        event = EventFactory()
        assert collect_event() == ((event.poster.email, event.created, EmailLastSeenKind.LOGGED),)

    def test_collect_DSP(self, db):
        dsp = DSPFactory()
        assert collect_DSP() == ((dsp.user.email, dsp.created, EmailLastSeenKind.LOGGED),)

    def test_upvote(self, db):
        upvote = UpVoteFactory(content_object=ForumFactory(), voter=UserFactory())
        assert collect_upvote() == ((upvote.voter.email, upvote.created_at, EmailLastSeenKind.LOGGED),)

    def test_forum_rating(self, db):
        ForumRatingFactory(user=None)
        forum_rating = ForumRatingFactory(user=UserFactory())
        assert collect_forum_rating() == ((forum_rating.user.email, forum_rating.created, EmailLastSeenKind.LOGGED),)

    def test_collect_post(self, db):
        topic = TopicFactory(with_post=True)
        anonymous_topic = AnonymousTopicFactory(with_post=True)

        assert collect_post() == (
            (topic.first_post.poster.email, topic.first_post.created, EmailLastSeenKind.POST),
            (anonymous_topic.first_post.username, anonymous_topic.first_post.created, EmailLastSeenKind.POST),
        )

    def test_collect_clicked_notifs(self, db):
        notification = NotificationFactory(visited_at=timezone.now())

        assert collect_clicked_notifs() == (
            (notification.recipient, notification.visited_at, EmailLastSeenKind.VISITED),
        )

    def test_collect_existing_email_last_seen(self, db):
        emails = ["undesired@test.com", "expected@test.com", "doesnotexists@test.com"]
        for email in emails[:2]:
            EmailLastSeenFactory(email=email)

        collected = list(collect_existing_email_last_seen(emails[1:]))
        expected = list(
            EmailLastSeen.objects.filter(email=emails[1]).values_list("email", "last_seen_at", "last_seen_kind")
        )
        assert collected == expected

    def test_keep_most_recent_tuple(self):
        emails = ["john@osborne.com", "mathilde@osborne.com"]
        now = timezone.now()
        tuples = [
            (emails[0], now, EmailLastSeenKind.LOGGED),
            (emails[0], now - relativedelta(days=5), EmailLastSeenKind.VISITED),
            (emails[0], now + relativedelta(days=10), EmailLastSeenKind.POST),
            (emails[1], now, EmailLastSeenKind.LOGGED),
        ]
        expected = {
            emails[0]: tuples[2],
            emails[1]: tuples[3],
        }
        assert keep_most_recent_tuple(tuples) == expected

    def test_insert_last_seen(self, db):
        emails = ["natacha@osborne.com", "pete@osborne.com"]
        EmailLastSeenFactory(email=emails[0], last_seen_kind=EmailLastSeenKind.VISITED)
        datas_to_insert = {
            emails[0]: (emails[0], timezone.now(), EmailLastSeenKind.LOGGED),
            emails[1]: (emails[1], timezone.now(), EmailLastSeenKind.POST),
        }
        insert_last_seen(datas_to_insert)

        assert EmailLastSeen.objects.count() == 2
        assert EmailLastSeen.objects.filter(email=emails[0], last_seen_kind=EmailLastSeenKind.LOGGED).exists()
        assert EmailLastSeen.objects.filter(email=emails[1], last_seen_kind=EmailLastSeenKind.POST).exists()

    def test_iterate_over_emails(self, db):
        size = 2
        EventFactory.create_batch(size * 2 + 1)
        iterate_over_emails(collect_event(), size=size)
        assert EmailLastSeen.objects.count() == size * 2 + 1

    def test_populate_emaillastseen_command(self, db):
        user = UserFactory(last_login=timezone.make_aware(datetime(2024, 10, 22)))
        event = EventFactory()
        dsp = DSPFactory()
        upvote = UpVoteFactory(content_object=ForumFactory(), voter=UserFactory())
        forum_rating = ForumRatingFactory(user=UserFactory())
        topic = TopicFactory(with_post=True)
        anonymous_topic = AnonymousTopicFactory(with_post=True)
        clicked_notification = NotificationFactory(visited_at=timezone.now())

        # existing email last seen
        EmailLastSeenFactory(email=dsp.user.email)

        # duplicated email
        EventFactory(poster__email=event.poster.email)

        call_command("populate_emaillastseen")

        assert EmailLastSeen.objects.count() == 8
        assert EmailLastSeen.objects.filter(email=user.email, last_seen_kind=EmailLastSeenKind.LOGGED).exists()
        assert EmailLastSeen.objects.filter(email=event.poster.email, last_seen_kind=EmailLastSeenKind.LOGGED).exists()
        assert EmailLastSeen.objects.filter(email=dsp.user.email, last_seen_kind=EmailLastSeenKind.LOGGED).exists()
        assert EmailLastSeen.objects.filter(email=upvote.voter.email, last_seen_kind=EmailLastSeenKind.LOGGED).exists()
        assert EmailLastSeen.objects.filter(
            email=forum_rating.user.email, last_seen_kind=EmailLastSeenKind.LOGGED
        ).exists()
        assert EmailLastSeen.objects.filter(
            email=topic.first_post.poster.email, last_seen_kind=EmailLastSeenKind.POST
        ).exists()
        assert EmailLastSeen.objects.filter(
            email=anonymous_topic.first_post.username, last_seen_kind=EmailLastSeenKind.POST
        ).exists()
        assert EmailLastSeen.objects.filter(
            email=clicked_notification.recipient, last_seen_kind=EmailLastSeenKind.VISITED
        ).exists()


class TestCreateMissyouNotifications:
    def test_create_missyou_notifications_command(self, db):
        expected = EmailLastSeenFactory(
            last_seen_at=timezone.now() - relativedelta(days=settings.EMAIL_LAST_SEEN_MISSYOU_DELAY)
        )
        EmailLastSeenFactory(
            last_seen_at=timezone.now() - relativedelta(days=settings.EMAIL_LAST_SEEN_MISSYOU_DELAY),
            missyou_send_at=timezone.now(),
        )
        unexpected = EmailLastSeenFactory(last_seen_at=timezone.now())

        call_command("add_missyou_notifications")
        notification = Notification.objects.get()
        assert notification.recipient == expected.email
        assert notification.kind == EmailSentTrackKind.MISSYOU
        assert notification.delay == NotificationDelay.ASAP

        expected.refresh_from_db()
        assert expected.missyou_send_at is not None
        unexpected.refresh_from_db()
        assert unexpected.missyou_send_at is None

    def test_create_missyou_notification_command_batch_size(self, db):
        EmailLastSeenFactory.create_batch(
            settings.EMAIL_LAST_SEEN_MISSYOU_BATCH_SIZE + 1,
            last_seen_at=timezone.now() - relativedelta(days=settings.EMAIL_LAST_SEEN_MISSYOU_DELAY),
        )
        call_command("add_missyou_notifications")
        assert Notification.objects.count() == settings.EMAIL_LAST_SEEN_MISSYOU_BATCH_SIZE
        assert (
            EmailLastSeen.objects.filter(missyou_send_at__isnull=False).count()
            == settings.EMAIL_LAST_SEEN_MISSYOU_BATCH_SIZE
        )


class TestDatasAnonymisation:
    def test_datas_anonymisation_commmand(self, db):
        email_last_seen_list = EmailLastSeenFactory.create_batch(2, soft_deletable=True)
        user = UserFactory(email=email_last_seen_list[0].email)
        post = AnonymousPostFactory(topic=TopicFactory())
        EmailLastSeen.objects.filter(email=post.username).update(
            missyou_send_at=timezone.now() - relativedelta(days=settings.EMAIL_LAST_SEEN_ARCHIVE_PERSONNAL_DATAS_DELAY)
        )

        # undesired datas
        EmailLastSeenFactory()
        EmailLastSeenFactory(
            missyou_send_at=timezone.now()
            - relativedelta(days=settings.EMAIL_LAST_SEEN_ARCHIVE_PERSONNAL_DATAS_DELAY - 1)
        )

        call_command("datas_anonymisation")

        assert EmailLastSeen.objects.filter(deleted_at__isnull=False, email_hash__isnull=False).count() == 3
        user.refresh_from_db()
        assert user.email.startswith("email-anonymise-")
        post.refresh_from_db()
        assert post.username.startswith("email-anonymise-")
