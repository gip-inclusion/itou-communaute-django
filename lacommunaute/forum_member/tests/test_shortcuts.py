from django.test import TestCase

from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.users.factories import UserFactory


class GetForumMemberDisplayNameShortcutTest(TestCase):
    def test_returns_the_display_name_of_a_user(self):
        user = UserFactory.create()
        self.assertEqual(get_forum_member_display_name(user), f"{user.first_name} {user.last_name.capitalize()[0]}.")

    def test_returns_the_display_name_of_a_user_wo_firstname(self):
        user = UserFactory.create(first_name="")
        self.assertEqual(get_forum_member_display_name(user), f"{user.last_name.capitalize()[0]}.")

    def test_returns_the_display_name_of_a_user_wo_lastname(self):
        user = UserFactory.create(last_name="")
        self.assertEqual(get_forum_member_display_name(user), f"{user.first_name}")
