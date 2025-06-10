import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum_member.enums import ActiveSearch, Regions
from lacommunaute.forum_member.factories import ForumProfileFactory


@pytest.mark.parametrize(
    "arg_name,arg_value,query,assert_in",
    [
        pytest.param(
            "linkedin",
            "https://truc-muche.com",
            "has_linkedin=yes",
            assertContains,
            id="has-linkedin",
        ),
        pytest.param(
            "linkedin", "", "has_linkedin=yes", assertNotContains, id="without-linkedin"
        ),
        pytest.param(
            "cv", "https://truc-muche.com", "has_cv=yes", assertContains, id="has-cv"
        ),
        pytest.param("cv", "", "has_cv=yes", assertNotContains, id="without-cv"),
        pytest.param(
            "search",
            ActiveSearch.Internship,
            "search__exact=INTERNSHIP",
            assertContains,
            id="has-search",
        ),
        pytest.param(
            "search",
            ActiveSearch.NO,
            "search__exact=INTERNSHIP",
            assertNotContains,
            id="without-search",
        ),
        pytest.param(
            "region", Regions.R84, "region__exact=84", assertContains, id="has-region"
        ),
        pytest.param(
            "region", Regions.R84, "region__exact=13", assertNotContains, id="no-region"
        ),
    ],
)
@pytest.mark.django_db
def test_admin(arg_name, arg_value, query, assert_in, admin_client):
    profile = ForumProfileFactory(**{arg_name: arg_value})

    response = admin_client.get(
        reverse("admin:forum_member_forumprofile_changelist") + f"?{query}"
    )
    assert_in(response, profile.user.email)
