from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.views import PostDeleteView, TopicCreateView, TopicUpdateView, TopicView
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.users.factories import UserFactory


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class TopicCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poster = UserFactory()
        cls.forum = ForumFactory()
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
        topic = TopicFactory(forum=self.forum, poster=self.poster, with_post=True)
        view = TopicCreateView()
        view.forum_post = topic.posts.first()
        self.assertEqual(
            view.get_success_url(),
            reverse("forum_extension:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
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
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:topic_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "slug": cls.topic.slug,
                "pk": cls.topic.pk,
            },
        )
        assign_perm("can_read_forum", cls.poster, cls.topic.forum)
        assign_perm("can_see_forum", cls.poster, cls.topic.forum)

    def test_redirection(self):
        view = TopicUpdateView()
        view.forum_post = self.topic.posts.first()
        self.assertEqual(
            view.get_success_url(),
            reverse("forum_extension:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )

    def test_has_not_permission_to_delete_post(self):
        assign_perm("can_edit_own_posts", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.topic.slug,
                    "topic_pk": self.topic.pk,
                    "pk": self.topic.posts.first().pk,
                },
            ),
        )

    def test_has_permission_to_delete_post(self):
        assign_perm("can_edit_own_posts", self.poster, self.forum)
        assign_perm("can_delete_own_posts", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.topic.slug,
                    "topic_pk": self.topic.pk,
                    "pk": self.topic.posts.first().pk,
                },
            ),
        )

    def test_topic_is_marked_as_read_when_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        assign_perm("can_edit_own_posts", self.poster, self.forum)
        self.client.force_login(self.poster)

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
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.url = reverse(
            "forum_conversation:post_create",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "topic_slug": cls.topic.slug,
                "topic_pk": cls.topic.pk,
            },
        )

    def test_http_forbidden(self):

        self.client.force_login(self.poster)

        post_data = {"content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 403)


class PostUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:post_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "topic_slug": cls.topic.slug,
                "topic_pk": cls.topic.pk,
                "pk": cls.topic.posts.first().pk,
            },
        )
        assign_perm("can_read_forum", cls.poster, cls.forum)
        assign_perm("can_see_forum", cls.poster, cls.forum)
        assign_perm("can_edit_own_posts", cls.poster, cls.forum)

    def test_has_not_permission_to_delete_post(self):
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.topic.slug,
                    "topic_pk": self.topic.pk,
                    "pk": self.topic.posts.first().pk,
                },
            ),
        )

    def test_has_permission_to_delete_post(self):
        assign_perm("can_delete_own_posts", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.topic.slug,
                    "topic_pk": self.topic.pk,
                    "pk": self.topic.posts.first().pk,
                },
            ),
        )

    def test_topic_is_marked_as_read_when_post_is_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        self.client.force_login(self.poster)

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
        topic = TopicFactory(with_post=True)

        factory = RequestFactory()
        request = factory.get("/")
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        view = PostDeleteView()
        view.object = topic.posts.first()
        view.request = request
        self.assertEqual(
            view.get_success_url(),
            reverse("forum_extension:forum", kwargs={"pk": topic.forum.pk, "slug": topic.forum.slug}),
        )
        msgs = get_messages(request)
        self.assertTrue(view.success_message, msgs._queued_messages[0].message)


class TopicViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.perm_handler = PermissionHandler()
        assign_perm("can_read_forum", cls.poster, cls.topic.forum)
        assign_perm("can_see_forum", cls.poster, cls.topic.forum)
        cls.kwargs = {
            "forum_pk": cls.topic.forum.pk,
            "forum_slug": cls.topic.forum.slug,
            "pk": cls.topic.pk,
            "slug": cls.topic.slug,
        }
        cls.url = reverse("forum_conversation:topic", kwargs=cls.kwargs)

    def test_has_liked(self):
        self.topic.likers.add(self.poster)
        self.topic.save()

        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

    def test_has_not_liked(self):
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">0</span>')

    def test_pluralized_likes(self):
        self.topic.likers.add(UserFactory())
        self.topic.likers.add(UserFactory())
        self.topic.save()

        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">2</span>')

    def test_anonymous_like(self):
        assign_perm("can_read_forum", AnonymousUser(), self.topic.forum)
        params = {"next_url": self.url}
        url = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"

        response = self.client.get(self.url)
        self.assertContains(response, url)

        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertNotContains(response, url)

    def test_upvote_annotations_in_get_queryset(self):
        post = self.topic.posts.first()
        request = RequestFactory().get(self.url)
        request.user = self.poster
        view = TopicView()
        view.request = request
        view.kwargs = self.kwargs

        qs = view.get_queryset()
        self.assertEqual(qs.first().upvotes_count, 0)
        self.assertEqual(qs.first().has_upvoted, False)

        UpVoteFactory(post=post, voter=UserFactory())
        UpVoteFactory(post=post, voter=self.poster)

        qs = view.get_queryset()
        self.assertEqual(qs.first().upvotes_count, 2)
        self.assertEqual(qs.first().has_upvoted, True)

    def test_show_joboffer_applications(self):
        self.topic.type = Topic.TOPIC_JOBOFFER
        self.topic.save()
        posts = PostFactory.create_batch(2, topic=self.topic, poster=self.poster)

        # anonymous user is not topic poster cannot see applications
        assign_perm("can_see_forum", AnonymousUser(), self.topic.forum)
        assign_perm("can_read_forum", AnonymousUser(), self.topic.forum)
        response = self.client.get(self.url)
        self.assertContains(response, "déjà 2 candidatures")
        for post in posts:
            with self.subTest(post=post):
                self.assertNotContains(response, post.content)

        # user is not topic poster cannot see applications
        user = UserFactory()
        assign_perm("can_see_forum", user, self.topic.forum)
        assign_perm("can_read_forum", user, self.topic.forum)
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertContains(response, "déjà 2 candidatures")
        for post in posts:
            with self.subTest(post=post):
                self.assertNotContains(response, post.content)

        # user is topic poster can see applications
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertContains(response, "déjà 2 candidatures")
        self.assertContains(
            response,
            "vous êtes la seule personne à pouvoir consulter les candidatures associées à cette offre d'emploi",
        )
        for post in posts:
            with self.subTest(post=post):
                self.assertContains(response, post.content)
