import pytest  # noqa
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum.factories import CategoryForumFactory
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.surveys.models import DSP
from lacommunaute.users.factories import UserFactory


dsp_choices_list = [
    "work_capacity",
    "language_skills",
    "housing",
    "rights_access",
    "mobility",
    "resources",
    "judicial",
    "availability",
]

form_html = '<form method="post">'
tally_html = '<iframe data-tally-src="https://tally.so/embed'
login_with_next_url = reverse("inclusion_connect:authorize") + "?next=" + reverse("surveys:dsp_create")


class TestDSPCreateView:
    def test_user_is_not_authenticated(self, db, client):
        url = reverse("surveys:dsp_create")
        response = client.get(url)
        assertContains(response, login_with_next_url)
        assertContains(response, tally_html)
        assertNotContains(response, form_html)

    def test_user_has_no_permission(self, db, client):
        client.force_login(UserFactory())
        response = client.get(reverse("surveys:dsp_create"))
        assertContains(response, tally_html)
        assertNotContains(response, login_with_next_url)
        assertNotContains(response, form_html)

    def test_user_has_permission(self, db, client):
        client.force_login(UserFactory(with_perm=[Permission.objects.get(codename="add_dsp")]))
        response = client.get(reverse("surveys:dsp_create"))
        assertContains(response, form_html)
        assertNotContains(response, tally_html)
        assertNotContains(response, login_with_next_url)

    def test_form_fields(self, db, client):
        url = reverse("surveys:dsp_create")
        client.force_login(UserFactory())
        response = client.get(url)
        assert response.status_code == 200
        assert "form" in response.context
        for field in dsp_choices_list:
            assert field in response.context["form"].fields

    def test_related_forums(self, db, client):
        forum = CategoryForumFactory(with_child=True)
        url = reverse("surveys:dsp_create")
        with override_settings(DSP_FORUM_RELATED_ID=forum.id):
            response = client.get(url)
        for related_forum in forum.get_children():
            assertContains(response, related_forum.name)

    def test_form_valid(self, db, client):
        url = reverse("surveys:dsp_create")
        client.force_login(UserFactory())
        choices = {key: "0" for key in dsp_choices_list}
        response = client.post(url, choices)
        assert response.status_code == 302

        dsp = DSP.objects.get()
        assert response.url == reverse("surveys:dsp_detail", kwargs={"pk": dsp.pk})
        assert dsp.recommendations is not None


class TestDSPDetailView:
    def test_login_required(self, db, client):
        url = reverse("surveys:dsp_detail", kwargs={"pk": 1})
        response = client.get(url)
        assert response.status_code == 302

    def test_user_cannot_view_others_surveys(self, db, client):
        dsp = DSPFactory()
        client.force_login(UserFactory())
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp.pk})
        response = client.get(url)
        assert response.status_code == 404

    def test_user_can_view_own_survey(self, db, client):
        dsp = DSPFactory()
        client.force_login(dsp.user)
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp.pk})
        response = client.get(url)
        assert response.status_code == 200

    def test_related_forums(self, db, client):
        forum = CategoryForumFactory(with_child=True)
        dsp = DSPFactory()
        client.force_login(dsp.user)
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp.pk})
        with override_settings(DSP_FORUM_RELATED_ID=forum.id):
            response = client.get(url)
        for related_forum in forum.get_children():
            assertContains(response, related_forum.name)


class TestHomeView:
    def test_link_to_dsp(self, db, client):
        client.force_login(UserFactory())
        response = client.get(reverse("pages:home"))
        assertContains(response, reverse("surveys:dsp_create"))
