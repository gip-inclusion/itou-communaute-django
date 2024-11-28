import pytest

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import (
    AnonymousPostFactory,
    AnonymousTopicFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay, delay_of_notifications
from lacommunaute.notification.models import Notification
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="upvoter")
def fixture_upvoter():
    return UserFactory()


@pytest.fixture(name="topic_in_forum_with_upvoter")
def fixture_topic_in_forum_with_upvoter(upvoter):
    return TopicFactory(forum=ForumFactory(upvoted_by=[upvoter]), with_post=True)


class TestCreatePostNotifications:
    def test_pending_topic(self, db, topic_in_forum_with_upvoter, upvoter):
        notification = Notification.objects.get()

        for key, expected in [
            ("recipient", upvoter.email),
            ("post", topic_in_forum_with_upvoter.first_post),
            ("kind", EmailSentTrackKind.PENDING_TOPIC),
            ("delay", NotificationDelay.DAY),
        ]:
            assert getattr(notification, key) == expected

    def test_first_reply(self, db, topic_in_forum_with_upvoter):
        Notification.objects.all().delete()

        PostFactory(topic=topic_in_forum_with_upvoter)
        notification = Notification.objects.get()

        for key, expected in [
            ("recipient", topic_in_forum_with_upvoter.first_post.poster.email),
            ("post", topic_in_forum_with_upvoter.last_post),
            ("kind", EmailSentTrackKind.FIRST_REPLY),
            ("delay", NotificationDelay.ASAP),
        ]:
            assert getattr(notification, key) == expected

    def test_first_reply_on_anonymous_topic(self, db):
        topic = AnonymousTopicFactory(with_post=True)
        Notification.objects.all().delete()

        PostFactory(topic=topic)
        notification = Notification.objects.get()

        for key, expected in [
            ("recipient", topic.first_post.username),
            ("post", topic.last_post),
            ("kind", EmailSentTrackKind.FIRST_REPLY),
            ("delay", NotificationDelay.ASAP),
        ]:
            assert getattr(notification, key) == expected

    def test_following_replies(self, db, topic_in_forum_with_upvoter):
        first_reply_poster = UserFactory()
        PostFactory(topic=topic_in_forum_with_upvoter, poster=first_reply_poster)
        Notification.objects.all().delete()

        PostFactory(topic=topic_in_forum_with_upvoter)

        assert Notification.objects.count() == 2

        for notification in Notification.objects.all():
            assert notification.recipient in [
                topic_in_forum_with_upvoter.first_post.poster.email,
                first_reply_poster.email,
            ]
            for key, expected in [
                ("post", topic_in_forum_with_upvoter.last_post),
                ("kind", EmailSentTrackKind.FOLLOWING_REPLIES),
                ("delay", NotificationDelay.DAY),
            ]:
                assert getattr(notification, key) == expected

    def test_following_replies_on_anonymous_topic(self, db):
        topic = AnonymousTopicFactory(with_post=True)
        post = AnonymousPostFactory(topic=topic)
        Notification.objects.all().delete()

        PostFactory(topic=topic)
        assert Notification.objects.count() == 2

        for notification in Notification.objects.all():
            assert notification.recipient in [topic.first_post.username, post.username]
            for key, expected in [
                ("post", topic.last_post),
                ("kind", EmailSentTrackKind.FOLLOWING_REPLIES),
                ("delay", NotificationDelay.DAY),
            ]:
                assert getattr(notification, key) == expected

    def test_no_notifications_on_unapproved_post(self, db, upvoter):
        topic = TopicFactory(forum=ForumFactory(upvoted_by=[upvoter]))

        for _ in delay_of_notifications:
            PostFactory(topic=topic, approved=False)
            assert Notification.objects.count() == 0
