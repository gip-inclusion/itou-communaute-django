from django.urls import reverse
from pytest_django.asserts import assertContains, assertTemplateUsed

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


url = reverse("forum_upvote:mine")


def test_anonymous_user(client, db):
    response = client.get(url)
    assert response.status_code == 302


def test_authenticated_user(client, db):
    client.force_login(UserFactory())
    response = client.get(url)
    assert response.status_code == 200
    assertTemplateUsed(response, "forum_upvote/upvote_list.html")


def test_pagination(client, db):
    user = UserFactory()
    client.force_login(user)

    response = client.get(url)
    assertContains(response, "Aucun résultat", status_code=200)
    assert response.context["paginator"].per_page == 10
    assert response.context_data["upvotes"].count() == 0

    # add upvote
    ForumFactory(upvoted_by=[user])

    response = client.get(url)
    assert response.status_code == 200
    assert response.context_data["upvotes"].count() == 1
    assert response.context_data["page_obj"].has_next() is False

    # add 10 upvotes
    ForumFactory.create_batch(10, upvoted_by=[user])

    response = client.get(url)
    assert response.status_code == 200
    assert response.context_data["upvotes"].count() == 10
    assert response.context_data["page_obj"].has_next() is True


def test_upvoted_forum(client, db):
    user = UserFactory()
    client.force_login(user)

    forum = ForumFactory(upvoted_by=[user])

    response = client.get(url)
    assertContains(response, forum.get_absolute_url(), status_code=200)
    assertContains(response, forum.name, status_code=200)
    # assert forum.get_absolute_url() in response.content.decode("utf-8")


def test_upvoted_post(client, db):
    user = UserFactory()
    client.force_login(user)

    post = PostFactory(topic=TopicFactory(), upvoted_by=[user])

    response = client.get(url)
    assertContains(response, post.topic.subject, status_code=200)
    assertContains(response, post.topic.get_absolute_url(), status_code=200)


def test_numqueries(client, db, django_assert_num_queries):
    user = UserFactory()
    client.force_login(user)

    ForumFactory.create_batch(20, upvoted_by=[user])
    PostFactory.create_batch(20, topic=TopicFactory(), upvoted_by=[user])

    # vincentporte : to be optimized
    with django_assert_num_queries(38):
        client.get(url)
