import uuid

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum

from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.users.factories import DEFAULT_PASSWORD, UserFactory


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class ForumProfileListViewTest(TestCase):
    def test_ForumProfileListView(self):
        forum_profiles = ForumProfileFactory.create_batch(2)
        response = self.client.get(reverse("members:profiles"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["forum_profiles"]), ForumProfile.objects.count())

        for forum_profile in forum_profiles:
            with self.subTest(forum_profile=forum_profile):
                self.assertContains(response, forum_profile.user.first_name)
                self.assertContains(
                    response,
                    # legacy machina reversed url
                    reverse("forum_member:profile", kwargs={"pk": forum_profile.user_id}),
                )


class JoinForumLandingView(TestCase):
    def test_token_doesnt_exists(self):
        user = UserFactory()
        wrong_token = uuid.uuid4()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        url = reverse("members:join_forum_form", kwargs={"token": wrong_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/404.html")


class JoinForumFormViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.token = uuid.uuid4()
        cls.forum = create_forum(invitation_token=cls.token)
        cls.forum.members_group = Group.objects.create(name="members")
        cls.forum.save()
        cls.user = UserFactory()
        cls.url = reverse("members:join_forum_form", kwargs={"token": cls.token})

        cls.perm_handler = PermissionHandler()
        assign_perm("can_read_forum", cls.forum.members_group, cls.forum)
        assign_perm("can_see_forum", cls.forum.members_group, cls.forum)

    def test_anonymous_redirection(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response, reverse("members:join_forum_landing", kwargs={"token": self.token}) + "?next=" + self.url
        )

    def test_token_doesnt_exists(self):
        wrong_token = uuid.uuid4()
        self.client.force_login(self.user)
        url = reverse("members:join_forum_form", kwargs={"token": wrong_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/404.html")

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.forum.name)

    def test_post(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse(
                "forum:forum",
                kwargs={
                    "slug": self.forum.slug,
                    "pk": self.forum.pk,
                },
            ),
        )
        self.assertTrue(self.forum.members_group.user_set.filter(id=self.user.id).exists())

    def test_already_in_group(self):
        self.forum.members_group.user_set.add(self.user)
        self.client.force_login(self.user)
        self.client.post(self.url)
        self.assertTrue(self.forum.members_group.user_set.filter(id=self.user.id).exists())
