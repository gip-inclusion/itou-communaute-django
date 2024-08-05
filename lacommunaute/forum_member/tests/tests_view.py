from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase
from django.urls import reverse
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.forum_member.views import ForumProfileUpdateView
from lacommunaute.users.factories import UserFactory


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class ForumProfileUpdateViewTest(TestCase):
    def test_success_url(self):
        forum_profiles = ForumProfileFactory()
        view = ForumProfileUpdateView()
        view.request = RequestFactory().get("/")
        view.request.user = forum_profiles.user
        self.assertEqual(
            view.get_success_url(), reverse("members:profile", kwargs={"username": forum_profiles.user.username})
        )

    def test_form_fields(self):
        forum_profiles = ForumProfileFactory()
        self.client.force_login(forum_profiles.user)
        response = self.client.get(reverse("members:profile_update"))

        self.assertContains(response, "linkedin", status_code=200)
        self.assertContains(response, "cv")
        self.assertContains(response, "search")
        self.assertContains(response, "region")
        self.assertContains(response, "internship_duration")


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
        self.assertContains(response, reverse("members:profile", kwargs={"username": forum_profile.user.username}))

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

    def test_queries_number(self):
        profiles = ForumProfileFactory.create_batch(10)
        self.forum.members_group.user_set.add(*[profile.user for profile in profiles])
        self.forum.members_group.save()

        self.client.force_login(self.profile.user)
        with self.assertNumQueries(11):
            self.client.get(self.url)


class TestSeekersListView:
    def test_content(self, client, db):
        undesired_forum_profile = ForumProfileFactory()
        internship_forum_profile = ForumProfileFactory(search="INTERNSHIP")
        apprentice_forum_profile = ForumProfileFactory(search="APPRENTICESHIP")

        response = client.get(reverse("members:seekers"))
        assertContains(response, get_forum_member_display_name(internship_forum_profile.user))
        assertContains(response, get_forum_member_display_name(apprentice_forum_profile.user))
        assertNotContains(response, get_forum_member_display_name(undesired_forum_profile.user))
        assert response.context_data["subtitle"] == "CIP en recherche active de stage ou d'alternance"

    def test_sorted_profils(self, client, db):
        ForumProfileFactory(search="APPRENTICESHIP")
        ForumProfileFactory(search="INTERNSHIP")
        response = client.get(reverse("members:seekers"))
        # test queryset is ordered by updated_at
        assert response.context_data["forum_profiles"][0] == ForumProfile.objects.last()
        assert response.context_data["forum_profiles"][1] == ForumProfile.objects.first()


class TestForumProfileDetailView:
    def test_show_linkedin_link(self, client, db):
        forum_profile = ForumProfileFactory(linkedin="https://www.linkedin.com/in/johndoe/")
        response = client.get(reverse("members:profile", kwargs={"username": forum_profile.user.username}))
        assertContains(response, forum_profile.linkedin)
