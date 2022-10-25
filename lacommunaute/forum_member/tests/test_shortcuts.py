from django.test import TestCase
from machina.core.loading import get_class

from lacommunaute.users.factories import UserFactory


get_forum_member_display_name = get_class("forum_member.shortcuts", "get_forum_member_display_name")


class TestGetForumMemberDisplayNameShortcut(TestCase):
    def test_returns_the_display_name_of_a_user(self):
        user = UserFactory.create()
        self.assertEqual(get_forum_member_display_name(user), f"{user.first_name} {user.last_name.capitalize()[0]}.")

    def test_returns_the_display_name_of_a_user_wo_firstname(self):
        user = UserFactory.create(first_name="")
        self.assertEqual(get_forum_member_display_name(user), f"{user.last_name.capitalize()[0]}.")

    def test_returns_the_display_name_of_a_user_wo_lastname(self):
        user = UserFactory.create(last_name="")
        self.assertEqual(get_forum_member_display_name(user), f"{user.first_name}")
