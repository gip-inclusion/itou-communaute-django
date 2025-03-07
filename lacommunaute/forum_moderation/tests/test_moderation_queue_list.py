import pytest
from django.urls import reverse

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.mark.parametrize(
    "topic", [lambda: TopicFactory(with_post=True), lambda: TopicFactory(with_post=True, answered=True)]
)
def test_subject_in_list(client, db, topic):
    client.force_login(UserFactory(is_superuser=True))
    post = topic().last_post
    post.approved = False
    post.save()
    response = client.get(reverse("forum_moderation:queue"))
    content = parse_response_to_soup(response, selector="#post-name")
    assert post.subject in str(content)
