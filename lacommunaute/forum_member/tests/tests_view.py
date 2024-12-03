import pytest
from django.test import RequestFactory, TestCase
from django.urls import reverse
from machina.core.loading import get_class
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.forum_member.views import ForumProfileUpdateView
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


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

    @pytest.mark.parametrize("authenticated,snapshot_name", [(True, "authenticated_user"), (False, "anonymous_user")])
    def test_update_profil_link(self, client, db, authenticated, snapshot_name, snapshot):
        if authenticated:
            client.force_login(UserFactory())
        response = client.get(reverse("members:seekers"))
        content = parse_response_to_soup(response, selector="#action-box")
        assert str(content) == snapshot(name=snapshot_name)


class TestForumProfileDetailView:
    def test_show_linkedin_link(self, client, db):
        forum_profile = ForumProfileFactory(linkedin="https://www.linkedin.com/in/johndoe/")
        response = client.get(reverse("members:profile", kwargs={"username": forum_profile.user.username}))
        assertContains(response, forum_profile.linkedin)
