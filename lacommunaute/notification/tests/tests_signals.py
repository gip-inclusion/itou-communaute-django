from django.test import TestCase

from lacommunaute.forum_conversation.factories import (
    AnonymousTopicFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.models import Notification
from lacommunaute.users.factories import UserFactory


class PostCreatedTest(TestCase):
    def test_notifications_on_post_creation(self):
        topic = TopicFactory(with_post=True)
        assert Notification.objects.count() == 0

        first_post = PostFactory(topic=topic)
        notification = Notification.objects.get()
        assert notification.recipient == topic.poster.email
        assert notification.post == first_post
        assert notification.kind == EmailSentTrackKind.FIRST_REPLY
        assert notification.delay == NotificationDelay.ASAP

        PostFactory(topic=topic)
        notifs = Notification.objects.exclude(id=notification.id)
        assert notifs.count() == 2
        assert notifs.exclude(post=first_post).count() == 2
        assert notifs.exclude(kind=EmailSentTrackKind.FOLLOWING_REPLIES).count() == 0
        assert notifs.exclude(delay=NotificationDelay.DAY).count() == 0
        anticipated_recipients = set({topic.poster.email, first_post.poster.email})
        assert set(notifs.values_list("recipient", flat=True)) == anticipated_recipients

    def test_notifications_on_post_creation_upvote_follower(self):
        topic = TopicFactory(with_post=True)

        upvoter = UserFactory()
        UpVote.objects.create(content_object=topic.first_post, voter=upvoter)

        post = PostFactory(topic=topic)
        notification = Notification.objects.get(recipient=upvoter.email)
        assert notification.post == post
        assert notification.kind == EmailSentTrackKind.FIRST_REPLY
        assert notification.delay == NotificationDelay.ASAP

    def test_notifications_on_post_creation_anonymous_poster(self):
        topic = AnonymousTopicFactory(with_post=True)

        post = PostFactory(topic=topic)
        notification = Notification.objects.get(recipient=topic.first_post.username)
        assert notification.post == post
        assert notification.kind == EmailSentTrackKind.FIRST_REPLY
        assert notification.delay == NotificationDelay.ASAP

    def test_notifications_no_approved_post(self):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic, approved=False)
        assert Notification.objects.count() == 0
