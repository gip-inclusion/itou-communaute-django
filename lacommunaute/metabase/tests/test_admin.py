import pytest  # noqa: F401
from django.urls import reverse
from pytest_django.asserts import assertNotContains

from lacommunaute.metabase.factories import ForumTableFactory


@pytest.mark.django_db
def test_add_button_hidden_on_admin_page_for_forumtable(admin_client):
    response = admin_client.get(reverse("admin:metabase_forumtable_changelist"))
    assertNotContains(response, reverse("admin:metabase_forumtable_add"), status_code=200)


@pytest.mark.django_db
def test_fields_are_readonly(admin_client):
    forumtable = ForumTableFactory()
    response = admin_client.get(reverse("admin:metabase_forumtable_change", kwargs={"object_id": forumtable.pk}))
    assert response.status_code == 200
    assert not response.context_data["adminform"].form.fields
