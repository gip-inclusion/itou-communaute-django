import pytest  # noqa
from django.urls import reverse

from lacommunaute.documentation.factories import DocumentFactory, DocumentRatingFactory
from lacommunaute.documentation.models import DocumentRating
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="document")
def fixture_document(db):
    return DocumentFactory()


@pytest.fixture(name="url")
def fixture_url(document):
    return reverse(
        "documentation:document_rate",
        kwargs={"category_pk": document.category.pk, "pk": document.pk, "slug": document.slug},
    )


@pytest.mark.parametrize("method", ["get", "delete", "put", "patch", "head", "trace"])
def test_forbidden_methods(url, client, method):
    response = getattr(client, method)(url)
    assert response.status_code == 405


@pytest.mark.parametrize(
    "user,expected_snapshot",
    [(None, "anonymous_post_document_rating"), (lambda: UserFactory(), "user_post_document_rating")],
)
def test_post_rating(client, url, document, user, expected_snapshot, snapshot):
    client.session.save()
    if user:
        user = user()
        client.force_login(user)

    response = client.post(url, data={"rating": 5})
    assert response.status_code == 200
    content = parse_response_to_soup(response)
    assert str(content) == snapshot(name=expected_snapshot)

    document_rating = DocumentRating.objects.get()
    assert document_rating.document == document
    if user:
        assert document_rating.user == user
    else:
        assert document_rating.user is None
    assert document_rating.rating == 5
    assert document_rating.session_id == client.session.session_key


def test_context_and_annotations(client, url, document):
    DocumentRatingFactory.create_batch(3, document=document, rating=1)
    DocumentRatingFactory.create_batch(2, document=document, rating=5)
    client.force_login(UserFactory())

    response = client.post(url, data={"rating": 5})
    assert response.status_code == 200
    assert response.context["count"] == 6
    assert response.context["average"] == 3
    assert response.context["rating"] == 5
