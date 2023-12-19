import pytest  # noqa
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

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


class TestDSPCreateView:
    def test_login_required(self, db, client):
        url = reverse("surveys:dsp_create")
        response = client.get(url)
        assert response.status_code == 302

    def test_form_fields(self, db, client):
        url = reverse("surveys:dsp_create")
        client.force_login(UserFactory())
        response = client.get(url)
        assert response.status_code == 200
        assert "form" in response.context
        for field in dsp_choices_list:
            assert field in response.context["form"].fields

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
        assert "form" in response.context
        assert "recommendations" in response.context


class TestHomeView:
    def test_link_to_dsp(self, db, client):
        user = UserFactory()
        client.force_login(user)
        url = reverse("pages:home")
        response = client.get(url)
        assert response.status_code == 200
        assertNotContains(response, reverse("surveys:dsp_create"))

        user.is_superuser = True
        user.save()
        response = client.get(url)
        assert response.status_code == 200
        assertContains(response, reverse("surveys:dsp_create"))
