import pytest
from django.urls import reverse

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="documentation_forum")
def fixture_documentation_forum():
    category_forum = CategoryForumFactory(with_public_perms=True, for_snapshot=True, name="Category Forum")
    ForumFactory(
        parent=category_forum,
        with_public_perms=True,
        with_image=True,
        with_tags=["Jazz", "Blues"],
        for_snapshot=True,
        name="Ella Fitzgerald",
    )
    ForumFactory(
        parent=category_forum, with_public_perms=True, with_image=True, for_snapshot=True, name="Mayra Andrade"
    )
    return category_forum


def test_listview_filtering(client, db, documentation_forum, snapshot):
    response = client.get(
        reverse(
            "forum_extension:subcategory_forums",
            kwargs={"slug": documentation_forum.slug, "pk": documentation_forum.pk},
        )
    )
    assert response.status_code == 200
    content = parse_response_to_soup(
        response, replace_in_href=documentation_forum.get_descendants(include_self=True), replace_img_src=True
    )
    assert str(content) == snapshot(name="subcategoryforum_listview_without_filter")

    response = client.get(
        reverse(
            "forum_extension:subcategory_forums",
            kwargs={"slug": documentation_forum.slug, "pk": documentation_forum.pk},
        )
        + "?forum_tag=rock"
    )
    assert response.status_code == 200
    content = parse_response_to_soup(
        response, replace_in_href=documentation_forum.get_descendants(include_self=True), replace_img_src=True
    )
    assert str(content) == snapshot(name="subcategoryforum_listview_filtering_on_non_existing_tag")

    response = client.get(
        reverse(
            "forum_extension:subcategory_forums",
            kwargs={"slug": documentation_forum.slug, "pk": documentation_forum.pk},
        )
        + "?forum_tag=jazz"
    )
    assert response.status_code == 200
    content = parse_response_to_soup(
        response, replace_in_href=documentation_forum.get_descendants(include_self=True), replace_img_src=True
    )
    assert str(content) == snapshot(name="subcategoryforum_listview_filtering_on_existing_tag")
