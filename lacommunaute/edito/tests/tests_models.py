import pytest  # noqa

from lacommunaute.edito.models import Edito


class TestEditoModel:
    def test_ordering(self):
        assert Edito._meta.ordering == ["-updated"]
