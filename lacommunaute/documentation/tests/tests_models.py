import pytest  # noqa
from django.db.utils import IntegrityError
from lacommunaute.documentation.factories import CategoryFactory, DocumentFactory


class TestCategory:
    def test_slug(self, db):
        category = CategoryFactory(for_snapshot=True)
        assert category.slug == "test-category"

    def test_slug_is_unique(self, db):
        CategoryFactory(for_snapshot=True)
        with pytest.raises(IntegrityError):
            CategoryFactory(for_snapshot=True)


class TestDocument:
    def test_slug(self, db):
        document = DocumentFactory(for_snapshot=True)
        assert document.slug == "test-document"

    def test_slug_is_unique(self, db):
        DocumentFactory(for_snapshot=True)
        with pytest.raises(IntegrityError):
            DocumentFactory(for_snapshot=True)
