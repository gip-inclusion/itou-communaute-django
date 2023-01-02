from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.views import PostCreateView, PostDeleteView, TopicCreateView, TopicUpdateView
from lacommunaute.users.factories import UserFactory


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


def build_post_in_forum():
    topic = TopicFactory(with_post=True)
    return topic.first_post


class TopicCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poster = UserFactory()
        cls.forum = create_forum()
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:topic_create",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
            },
        )
        assign_perm("can_read_forum", cls.poster, cls.forum)
        assign_perm("can_see_forum", cls.poster, cls.forum)

    def test_redirection(self):
        self.post = build_post_in_forum()
        self.forum = self.post.topic.forum
        view = TopicCreateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )

    def test_delete_button_is_hidden(self):
        assign_perm("can_start_new_topics", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, '/post/delete/" title="Supprimer" role="button" class="btn btn-outline-danger">Supprimer</a>'
        )

    def test_topic_is_marked_as_read_when_created(self):
        self.assertFalse(TopicReadTrack.objects.count())

        assign_perm("can_start_new_topics", self.poster, self.forum)
        self.client.force_login(self.poster)

        post_data = {"subject": "s", "content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, TopicReadTrack.objects.count())


class TopicUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = build_post_in_forum()
        cls.forum = cls.post.topic.forum
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:topic_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "slug": cls.post.topic.slug,
                "pk": cls.post.topic.pk,
            },
        )
        assign_perm("can_read_forum", cls.post.poster, cls.post.topic.forum)
        assign_perm("can_see_forum", cls.post.poster, cls.post.topic.forum)

    def test_redirection(self):
        view = TopicUpdateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )

    def test_has_not_permission_to_delete_post(self):
        assign_perm("can_edit_own_posts", self.post.poster, self.forum)
        self.client.force_login(self.post.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.post.topic.slug,
                    "topic_pk": self.post.topic.pk,
                    "pk": self.post.pk,
                },
            ),
        )

    def test_has_permission_to_delete_post(self):
        assign_perm("can_edit_own_posts", self.post.poster, self.forum)
        assign_perm("can_delete_own_posts", self.post.poster, self.forum)
        self.client.force_login(self.post.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.post.topic.slug,
                    "topic_pk": self.post.topic.pk,
                    "pk": self.post.pk,
                },
            ),
        )

    def test_topic_is_marked_as_read_when_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        assign_perm("can_edit_own_posts", self.post.poster, self.forum)
        self.client.force_login(self.post.poster)

        post_data = {"subject": "s", "content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ForumReadTrack.objects.count())


class PostCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = build_post_in_forum()
        cls.forum = cls.post.topic.forum
        cls.perm_handler = PermissionHandler()
        assign_perm("can_read_forum", cls.post.poster, cls.post.topic.forum)
        assign_perm("can_see_forum", cls.post.poster, cls.post.topic.forum)
        assign_perm("can_reply_to_topics", cls.post.poster, cls.post.topic.forum)
        cls.url = reverse(
            "forum_conversation:post_create",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "topic_slug": cls.post.topic.slug,
                "topic_pk": cls.post.topic.pk,
            },
        )

    def test_redirection(self):
        view = PostCreateView()
        view.forum_post = self.post
        self.assertEqual(
            view.get_success_url(),
            reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )

    def test_topic_is_marked_as_read_when_post_is_created(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        self.client.force_login(self.post.poster)

        post_data = {"content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ForumReadTrack.objects.count())

    def test_postform_in_context(self):
        self.client.force_login(self.post.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data["post_form"], PostForm)


class PostUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = build_post_in_forum()
        cls.forum = cls.post.topic.forum
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:post_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "topic_slug": cls.post.topic.slug,
                "topic_pk": cls.post.topic.pk,
                "pk": cls.post.pk,
            },
        )
        assign_perm("can_read_forum", cls.post.poster, cls.post.topic.forum)
        assign_perm("can_see_forum", cls.post.poster, cls.post.topic.forum)
        assign_perm("can_edit_own_posts", cls.post.poster, cls.forum)

    def test_has_not_permission_to_delete_post(self):
        self.client.force_login(self.post.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.post.topic.slug,
                    "topic_pk": self.post.topic.pk,
                    "pk": self.post.pk,
                },
            ),
        )

    def test_has_permission_to_delete_post(self):
        assign_perm("can_delete_own_posts", self.post.poster, self.forum)
        self.client.force_login(self.post.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.post.topic.slug,
                    "topic_pk": self.post.topic.pk,
                    "pk": self.post.pk,
                },
            ),
        )

    def test_topic_is_marked_as_read_when_post_is_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        self.client.force_login(self.post.poster)

        post_data = {"content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ForumReadTrack.objects.count())


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
        cls.kwargs = {
            "forum_pk": cls.post.topic.forum.pk,
            "forum_slug": cls.post.topic.forum.slug,
            "pk": cls.post.topic.pk,
            "slug": cls.post.topic.slug,
        }
        cls.url = reverse("forum_conversation:topic", kwargs=cls.kwargs)

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
