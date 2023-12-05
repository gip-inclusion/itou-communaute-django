import pytest  # noqa: F401
from django.core.management import call_command

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.metabase.factories import ForumTableFactory, PostTableFactory
from lacommunaute.metabase.models import ForumTable, PostTable
from lacommunaute.users.factories import UserFactory


@pytest.mark.django_db
def test_extract_forum_tables_command():
    upvoted_forum = ForumFactory(upvoted_by=[UserFactory()])
    TopicFactory(forum=upvoted_forum, with_post=True)

    category_forum_with_child = CategoryForumFactory(with_child=True, description=None, short_description=None)

    call_command("extract_tables")

    assert ForumTable.objects.count() == 3
    assert ForumTable.objects.filter(name=upvoted_forum.name).exists()
    assert ForumTable.objects.filter(name=category_forum_with_child.name).exists()
    assert ForumTable.objects.filter(name=category_forum_with_child.get_children().first().name).exists()

    upvoted_forum_table = ForumTable.objects.get(name=upvoted_forum.name)
    assert upvoted_forum_table.short_description_boolean
    assert upvoted_forum_table.description_boolean
    assert upvoted_forum_table.upvotes_count == 1
    assert upvoted_forum_table.parent_name is None

    category_forum_table = ForumTable.objects.get(name=category_forum_with_child.name)
    assert category_forum_table.short_description_boolean is False
    assert category_forum_table.description_boolean is False
    assert category_forum_table.upvotes_count == 0
    assert category_forum_table.parent_name is None

    child_forum_table = ForumTable.objects.get(name=category_forum_with_child.get_children().first().name)
    assert child_forum_table.parent_name == category_forum_with_child.name


@pytest.mark.django_db
def test_truncate_forum_table():
    ForumTableFactory()
    assert ForumTable.objects.count() == 1
    call_command("extract_tables")
    assert ForumTable.objects.count() == 0


@pytest.mark.django_db
def test_truncate_post_table():
    PostTableFactory()
    assert PostTable.objects.count() == 1
    call_command("extract_tables")
    assert PostTable.objects.count() == 0
