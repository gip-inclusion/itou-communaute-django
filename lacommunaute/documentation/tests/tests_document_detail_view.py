import pytest

from lacommunaute.documentation.factories import DocumentFactory, DocumentRatingFactory
from lacommunaute.partner.factories import PartnerFactory
from lacommunaute.utils.testing import parse_response_to_soup  # noqa


# test avec/sans partenaire
# test certifiée/non certifiée
# test avec/sans tags


@pytest.fixture(name="document")
def fixture_document(db):
    document = DocumentFactory(for_snapshot=True)
    for titre, short_desc, desc in [(f"titre {i}", f"short desc {i}", f"desc {i}") for i in range(1, 4)]:
        DocumentFactory(category=document.category, name=titre, short_description=short_desc, description=desc)
    return document


@pytest.mark.parametrize(
    "setup_func, snapshot_name",
    [
        (lambda document: None, "document_detail_view"),
        (
            lambda document: setattr(document, "partner", PartnerFactory(for_snapshot=True)) or document.save(),
            "document_detail_view_with_partner",
        ),
        (lambda document: document.tags.add("tag"), "document_detail_view_with_tags"),
        (
            lambda document: setattr(document, "certified", True) or document.save(),
            "document_detail_view_with_certified_document",
        ),
    ],
)
def test_detail_view(client, db, document, snapshot, setup_func, snapshot_name):
    setup_func(document)
    response = client.get(document.get_absolute_url())
    assert response.status_code == 200
    replace_in_href = [
        (f"documentation/{document.category.pk}/", "documentation/[PK of Category]/"),
        (f"{document.category.slug}-{document.category.pk}", "[Slug of Category]-[PK of Category]"),
    ] + [(f"{doc.slug}-{doc.pk}", "[Slug of Document]-[PK of Document]") for doc in document.category.documents.all()]
    if document.partner:
        replace_in_href.append(
            (f"/{document.partner.slug}-{document.partner.pk}", "/[Slug of Partner]-[PK of Partner]")
        )
    content = parse_response_to_soup(
        response,
        selector="main",
        replace_img_src=True,
        replace_in_href=replace_in_href,
        replace_current_date_format="%d/%m/%Y",
    )
    assert str(content) == snapshot(name=snapshot_name)


def test_detail_view_with_rated_document(client, db, document, snapshot):
    client.session.save()
    DocumentRatingFactory(document=document, rating=3, session_id=client.session.session_key)

    response = client.get(document.get_absolute_url())
    assert response.status_code == 200
    content = parse_response_to_soup(response, selector="#rating-area")
    assert str(content) == snapshot(name="document_detail_view_with_rated_document")
