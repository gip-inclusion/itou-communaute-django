import uuid

from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum

from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.users.factories import DEFAULT_PASSWORD, UserFactory
from lacommunaute.www.forum_member.views import ForumProfileUpdateView


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class ForumProfileUpdateViewTest(TestCase):
    def test_success_url(self):
        forum_profiles = ForumProfileFactory()
        view = ForumProfileUpdateView()
        view.request = RequestFactory().get("/")
        view.request.user = forum_profiles.user
        self.assertEqual(view.get_success_url(), reverse("members:profile", kwargs={"pk": forum_profiles.user.pk}))


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
                    reverse("members:profile", kwargs={"pk": forum_profile.user_id}),
                )


class ModeratorProfileListView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.forum = create_forum()
        cls.forum.members_group = Group.objects.create(name="members")
        cls.forum.save()
        cls.profile = ForumProfileFactory()

        cls.url = reverse(
            "members:forum_profiles",
            kwargs={"pk": cls.forum.pk, "slug": cls.forum.slug},
        )

        cls.perm_handler = PermissionHandler()
        assign_perm("can_approve_posts", cls.profile.user, cls.forum)

    def test_access_page(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        assign_perm("can_approve_posts", user, self.forum)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_context_data(self):
        self.client.force_login(self.profile.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context_data["forum"], self.forum)
        self.assertEqual(response.context_data["paginator"].per_page, 60)

    def test_content(self):
        forum_profile = ForumProfileFactory(user__first_name="Jeff", user__last_name="Buckley")
        self.forum.members_group.user_set.add(forum_profile.user)
        self.forum.members_group.save()

        self.client.force_login(self.profile.user)
        response = self.client.get(self.url)
        self.assertContains(response, forum_profile.user.get_full_name())
        self.assertContains(response, reverse("members:profile", kwargs={"pk": forum_profile.user_id}))

    def test_ordering_and_count(self):
        self.forum.members_group.user_set.add(ForumProfileFactory(user__first_name="z").user)
        self.forum.members_group.user_set.add(ForumProfileFactory(user__first_name="a").user)
        self.forum.members_group.save()

        self.client.force_login(self.profile.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["forum_profiles"][0].user.first_name, "a")
        self.assertEqual(response.context["forum_profiles"][1].user.first_name, "z")
        self.assertContains(response, "2 membres")

    def test_profile_in_group(self):
        ForumProfileFactory(user__first_name="john_is_not_a_member")
        self.forum.members_group.user_set.add(ForumProfileFactory(user__first_name="bob_is_a_member").user)
        self.forum.members_group.save()

        self.client.force_login(self.profile.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["forum_profiles"][0].user.first_name, "bob_is_a_member")
        self.assertContains(response, "1 membre")

    def test_join_url_is_shown(self):
        self.client.force_login(self.profile.user)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            reverse(
                "members:join_forum_form",
                kwargs={
                    "token": self.forum.invitation_token,
                },
            ),
        )


class JoinForumLandingView(TestCase):
    def test_token_doesnt_exists(self):
        user = UserFactory()
        wrong_token = uuid.uuid4()
        self.client.login(username=user.username, password=DEFAULT_PASSWORD)
        url = reverse("members:join_forum_form", kwargs={"token": wrong_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


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
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")

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
