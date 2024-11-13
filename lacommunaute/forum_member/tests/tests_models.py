from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


def test_get_forum_member_display_name(db):
    forum_profile = ForumProfileFactory()
    assert forum_profile.__str__() == get_forum_member_display_name(forum_profile.user)
