import pytest  # noqa
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from lacommunaute.forum_conversation.factories import (  # noqa
    AnonymousPostFactory,
    AnonymousTopicFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


def test_get_forum_member_display_name(db):
    forum_profile = ForumProfileFactory()
    assert forum_profile.__str__() == get_forum_member_display_name(forum_profile.user)


def test_powerusers_forumprofile_queryset(db):
    # anonymous user with 3 posts within the last 30 days
    topic1 = AnonymousTopicFactory(with_post=True)
    AnonymousPostFactory.create_batch(2, topic=topic1, username=topic1.first_post.username)

    # authenticated user with 2 posts within the last 30 days
    forum_profile1 = ForumProfileFactory()
    topic2 = TopicFactory(with_post=True, poster=forum_profile1.user)
    PostFactory(topic=topic2, poster=forum_profile1.user)

    # authenticated user with 3 post before the last 30 days
    forum_profile2 = ForumProfileFactory()
    topic3 = TopicFactory(with_post=True, poster=forum_profile2.user)
    PostFactory(topic=topic3, poster=forum_profile2.user)
    for post in topic3.posts.all():
        post.created = timezone.now() - relativedelta(days=31)
        post.save()

    assert ForumProfile.objects.power_users().count() == 0

    # authenticated user with 3 posts within the last 30 days
    poweruser = ForumProfileFactory()
    topic4 = TopicFactory(with_post=True, poster=poweruser.user)
    PostFactory.create_batch(2, topic=topic4, poster=poweruser.user)

    # authenticated user with more than 3 posts within the last 30 days
    bigpoweruser = ForumProfileFactory()
    topic5 = TopicFactory(with_post=True, poster=bigpoweruser.user)
    PostFactory.create_batch(20, topic=topic5, poster=bigpoweruser.user)

    assert bigpoweruser == ForumProfile.objects.power_users().first()
    assert poweruser == ForumProfile.objects.power_users().last()
    assert ForumProfile.objects.power_users().count() == 2
