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

    def test_get_absolute_url(self, db):
        category = CategoryFactory()
        assert category.get_absolute_url() == f"/documentation/{category.slug}-{category.pk}/"

    def test_get_update_url(self, db):
        category = CategoryFactory()
        assert category.get_update_url() == f"/documentation/{category.slug}-{category.pk}/update/"


class TestDocument:
    def test_slug(self, db):
        document = DocumentFactory(for_snapshot=True)
        assert document.slug == "test-document"

    def test_slug_is_unique(self, db):
        DocumentFactory(for_snapshot=True)
        with pytest.raises(IntegrityError):
            DocumentFactory(for_snapshot=True)

    def test_get_absolute_url(self, db):
        document = DocumentFactory()
        assert document.get_absolute_url() == f"/documentation/{document.category.pk}/{document.slug}-{document.pk}/"
