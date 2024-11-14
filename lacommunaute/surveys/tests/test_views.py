from django.test import override_settings
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum.factories import CategoryForumFactory
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.surveys.models import DSP
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


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
location_field_list = ["location", "city_code"]

form_html = '<form method="post">'
login_with_next_url = reverse("users:login") + "?next=" + reverse("surveys:dsp_create")


class TestDSPCreateView:
    def test_user_is_not_authenticated(self, db, client):
        url = reverse("surveys:dsp_create")
        response = client.get(url)
        assertContains(response, login_with_next_url)
        assertNotContains(response, form_html)

    def test_user_is_authenticated(self, db, client):
        client.force_login(UserFactory())
        response = client.get(reverse("surveys:dsp_create"))
        assertContains(response, form_html)
        assertNotContains(response, login_with_next_url)

    def test_form_fields(self, db, client):
        url = reverse("surveys:dsp_create")
        client.force_login(UserFactory())
        response = client.get(url)
        assert response.status_code == 200
        assert "form" in response.context
        for field in dsp_choices_list + location_field_list:
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
        choices.update({"location": "Le Mans", "city_code": "72000"})
        response = client.post(url, choices)
        assert response.status_code == 302

        dsp = DSP.objects.get()
        assert response.url == reverse("surveys:dsp_detail", kwargs={"pk": dsp.pk})
        assert dsp.recommendations is not None

    def test_form_invalid(self, db, client):
        url = reverse("surveys:dsp_create")
        client.force_login(UserFactory())
        response = client.post(url, {})

        assert response.status_code == 200
        assert response.context["form"].is_valid() is False
        errors = response.context["form"].errors
        for field in dsp_choices_list + ["location"]:
            assert errors[field] == ["Ce champ est obligatoire."]


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

    def test_suggested_services(self, db, client, snapshot):
        user = UserFactory()

        dsp_min = DSPFactory(for_snapshot_level_min=True, recommendations=True, user=user)
        client.force_login(user)
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp_min.pk})
        response = client.get(url)
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="level_min")

        dsp_level_1 = DSPFactory(for_snapshot_level_1=True, recommendations=True, user=user)
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp_level_1.pk})
        response = client.get(url)
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="level_1")

        dsp_level_2 = DSPFactory(for_snapshot_level_2=True, recommendations=True, user=user)
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp_level_2.pk})
        response = client.get(url)
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="level_2")

        dsp_level_max = DSPFactory(for_snapshot_level_max=True, recommendations=True, user=user)
        url = reverse("surveys:dsp_detail", kwargs={"pk": dsp_level_max.pk})
        response = client.get(url)
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="level_max")


class TestHomeView:
    def test_link_to_dsp(self, db, client):
        client.force_login(UserFactory())
        response = client.get(reverse("pages:home"))
        assertContains(response, reverse("surveys:dsp_create"))
