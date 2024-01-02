import hashlib
from io import StringIO
from unittest.mock import patch

import pytest  # noqa: F401
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.utils.encoding import force_bytes

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum_conversation.factories import AnonymousPostFactory, PostFactory, TopicFactory
from lacommunaute.forum_conversation.forum_attachments.factories import AttachmentFactory
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
def test_extract_post_tables_command():
    topic = TopicFactory(with_certified_post=True)

    call_command("extract_tables")
    assert PostTable.objects.count() == 2  # 1 for the post of the topic, 1 for the certified post
    posttable = PostTable.objects.first()
    assert posttable.subject == topic.subject
    assert posttable.forum_name == topic.forum.name
    assert posttable.poster == topic.poster.username
    assert posttable.is_anonymous_post is False
    assert posttable.certifier is None  # post of the topic
    assert posttable.post_upvotes_count == 0
    assert posttable.attachments_count == 0
    assert posttable.tags_list == ""
    assert posttable.approved_boolean is True
    assert posttable.topic_created_at == topic.created
    assert posttable.post_created_at == topic.first_post.created
    assert posttable.post_position_in_topic == 1
    assert posttable.updates_count == 0
    assert posttable.post_last_updated_at == topic.first_post.updated

    certified_posttable = PostTable.objects.last()
    assert certified_posttable.certifier == topic.certified_post.user.username
    assert certified_posttable.post_position_in_topic == 2


@pytest.mark.django_db
def test_extract_anonymous_post_tables_command():
    topic = TopicFactory(with_post=True)
    post = AnonymousPostFactory(topic=topic)

    call_command("extract_tables")
    assert PostTable.objects.count() == 2
    posttable = PostTable.objects.last()
    assert posttable.is_anonymous_post is True
    assert posttable.poster == hashlib.sha256(post.username.encode("utf-8")).hexdigest()


@pytest.mark.django_db
def test_extract_anonymous_post_with_known_user_tables_command():
    topic = TopicFactory(with_post=True)
    user = UserFactory()
    AnonymousPostFactory(topic=topic, username=user.email)

    call_command("extract_tables")
    assert PostTable.objects.count() == 2
    posttable = PostTable.objects.last()
    assert posttable.is_anonymous_post is True
    assert posttable.poster == user.username


@pytest.mark.django_db
def test_extract_anonymous_post_without_username_tables_command():
    topic = TopicFactory(with_post=True)
    anonymous_post = AnonymousPostFactory(topic=topic, username=None)

    with pytest.raises(Exception) as e:
        call_command("extract_tables")
    assert str(e.value) == f"No username found for post {anonymous_post.id}"


@pytest.mark.django_db
def test_extract_upvoted_post_tables_command():
    topic = TopicFactory(with_post=True)
    PostFactory(topic=topic, upvoted_by=[UserFactory()])

    call_command("extract_tables")
    assert PostTable.objects.count() == 2

    posttable = PostTable.objects.first()
    assert posttable.post_upvotes_count == 0

    upvoted_posttable = PostTable.objects.last()
    assert upvoted_posttable.post_upvotes_count == 1


@override_settings(STORAGES={"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}})
@pytest.mark.django_db
def test_extract_post_with_attachments_tables_command():
    topic = TopicFactory(with_post=True)
    AttachmentFactory(post=topic.first_post, file=SimpleUploadedFile("test.pdf", force_bytes("file_content")))

    call_command("extract_tables")
    assert PostTable.objects.count() == 1
    posttable = PostTable.objects.first()
    assert posttable.attachments_count == 1


@pytest.mark.django_db
def test_extract_post_with_tags_tables_command():
    topic = TopicFactory(with_post=True)
    topic.tags.add("tag1", "tag2")

    call_command("extract_tables")
    assert PostTable.objects.count() == 1
    posttable = PostTable.objects.first()
    assert posttable.tags_list == "tag1, tag2"


@pytest.mark.django_db
def test_extract_post_with_updates_tables_command():
    topic = TopicFactory(with_post=True)
    PostFactory(topic=topic, updates_count=1)

    call_command("extract_tables")
    assert PostTable.objects.count() == 2
    posttable = PostTable.objects.first()
    assert posttable.updates_count == 0

    updated_posttable = PostTable.objects.last()
    assert updated_posttable.updates_count == 1


@pytest.mark.django_db
def test_extract_disapproved_post_tables_command():
    topic = TopicFactory(with_post=True)
    topic.first_post.approved = False
    topic.first_post.save()

    call_command("extract_tables")
    assert PostTable.objects.count() == 1
    posttable = PostTable.objects.first()
    assert posttable.approved_boolean is False


@pytest.mark.django_db
def test_extract_more_posts_than_batch_size():
    TopicFactory.create_batch(2, with_post=True)
    with patch("sys.stdout", new=StringIO()) as fake_stdout:
        call_command("extract_tables", batch_size=1)
    assert PostTable.objects.count() == 2
    stdout = fake_stdout.getvalue().strip()
    excepted_stdout = (
        "Extracted 2 forums.\nForums extracted.\nExtracted 1 posts."
        "\nExtracted 1 posts.\nPosts extracted.\nThat's all, folks!"
    )
    assert stdout == excepted_stdout


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
