from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from machina.test.factories.conversation import PostFactory, create_topic
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.views import (
    PostCreateView,
    PostDeleteView,
    PostUpdateView,
    TopicCreateView,
    TopicUpdateView,
)
from lacommunaute.users.factories import UserFactory


def build_post_in_forum():
    poster = UserFactory()
    return PostFactory(topic=create_topic(forum=create_forum(), poster=poster), poster=poster)


class TopicCreateViewTest(TestCase):
    def test_redirection(self):
        self.post = build_post_in_forum()
        self.forum = self.post.topic.forum
        view = TopicCreateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )


class TopicUpdateViewTest(TestCase):
    def test_redirection(self):
        self.post = build_post_in_forum()
        self.forum = self.post.topic.forum
        view = TopicUpdateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )


class PostCreateViewTest(TestCase):
    def test_redirection(self):
        self.post = build_post_in_forum()
        self.forum = self.post.topic.forum
        view = PostCreateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )


class PostUpdateViewTest(TestCase):
    def test_redirection(self):
        self.post = build_post_in_forum()
        self.forum = self.post.topic.forum
        view = PostUpdateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )


class PostDeleteViewTest(TestCase):
    def test_redirection(self):
        self.post = build_post_in_forum()
        self.forum = self.post.topic.forum

        factory = RequestFactory()
        request = factory.get("/")
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        view = PostDeleteView()
        view.object = self.post
        view.request = request
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )
        msgs = get_messages(request)
        self.assertTrue(view.success_message, msgs._queued_messages[0].message)
