import pytest
from django.test import override_settings
from django.urls import reverse
from pytest_django.asserts import assertContains

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


@pytest.fixture(name="dsp_create_url")
def fixture_dsp_create_url():
    return reverse("surveys:dsp_create")


@pytest.fixture(name="choices")
def fixture_choices():
    choices = {key: "0" for key in dsp_choices_list}
    choices.update({"location": "Le Mans", "city_code": "72000"})
    return choices


class TestDSPCreateView:
    def test_action_box(self, db, client, dsp_create_url, snapshot):
        response = client.get(dsp_create_url)
        content = parse_response_to_soup(response, selector="#action-box")
        assert str(content) == snapshot(name="action_box")

    def test_form_fields(self, db, client, dsp_create_url):
        client.force_login(UserFactory())
        response = client.get(dsp_create_url)
        assert response.status_code == 200
        assert "form" in response.context
        for field in dsp_choices_list + location_field_list:
            assert field in response.context["form"].fields

    def test_related_forums(self, db, client, dsp_create_url):
        forum = CategoryForumFactory(with_child=True)
        with override_settings(DSP_FORUM_RELATED_ID=forum.id):
            response = client.get(dsp_create_url)
        for related_forum in forum.get_children():
            assertContains(response, related_forum.name)

    def test_form_valid(self, db, client, choices, dsp_create_url):
        client.force_login(UserFactory())
        response = client.post(dsp_create_url, choices)
        assert response.status_code == 302

        dsp = DSP.objects.get()
        assert response.url == reverse("surveys:dsp_detail", kwargs={"pk": dsp.pk})
        assert dsp.recommendations is not None

    def test_form_invalid(self, db, client, dsp_create_url):
        client.force_login(UserFactory())
        response = client.post(dsp_create_url, {})

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
