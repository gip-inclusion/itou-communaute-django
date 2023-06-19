from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory


@pytest.fixture
def search_url():
    return reverse("forum_search_extension:search")


def test_recent_content_is_added_to_index(client, db, search_url):
    forum = ForumFactory(with_public_perms=True)
    TopicFactory(forum=forum, with_post=True)

    out = StringIO()
    call_command("update_index", age=1, stdout=out, stderr=StringIO())

    assert out.getvalue() == "Indexing 1 Thématiques\nIndexing 1 Messages\n"
