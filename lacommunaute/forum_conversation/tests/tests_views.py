from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from machina.core.loading import get_class
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


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


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


class TopicViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.perm_handler = PermissionHandler()
        cls.post = build_post_in_forum()
        assign_perm("can_read_forum", cls.user, cls.post.topic.forum)
        assign_perm("can_see_forum", cls.user, cls.post.topic.forum)
        cls.url = cls.post.topic.get_absolute_url()

    def test_has_liked(self):
        topic = self.post.topic
        topic.likers.add(self.user)
        topic.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i>')
        self.assertContains(response, "<span>1 like</span>")

    def test_has_not_liked(self):
        topic = self.post.topic
        topic.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i>')
        self.assertContains(response, "<span>0 like</span>")

    def test_pluralized_likes(self):
        topic = self.post.topic
        topic.likers.add(UserFactory())
        topic.likers.add(UserFactory())
        topic.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i>')
        self.assertContains(response, "<span>2 likes</span>")

    def test_anonymous_like(self):
        assign_perm("can_read_forum", AnonymousUser(), self.post.topic.forum)
        params = {"next_url": self.url}
        url = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"

        response = self.client.get(self.url)
        self.assertContains(response, url)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(response, url)
