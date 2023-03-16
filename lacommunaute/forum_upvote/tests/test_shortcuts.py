from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_upvote.shortcuts import can_certify_post
from lacommunaute.users.factories import UserFactory


class CanCertifyPostShortcutTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.forum = ForumFactory.create()

    def test_user_is_not_authenticated(self):
        self.assertFalse(can_certify_post(self.forum, AnonymousUser()))

    def test_forum_is_private(self):
        self.assertFalse(can_certify_post(ForumFactory.create(is_private=True), self.user))

    def test_user_is_not_in_the_forum_members_group(self):
        self.assertFalse(can_certify_post(self.forum, self.user))

    def test_user_is_in_the_forum_members_group(self):
        self.forum.members_group.user_set.add(self.user)
        self.assertTrue(can_certify_post(self.forum, self.user))

    def test_user_is_staff(self):
        self.user.is_staff = True
        self.assertTrue(can_certify_post(self.forum, self.user))
