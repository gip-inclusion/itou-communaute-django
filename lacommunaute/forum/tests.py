from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum
from machina.test.factories.permission import UserForumPermissionFactory

from lacommunaute.forum.views import ForumView
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


Topic = get_model("forum_conversation", "Topic")
ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class ForumViewQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.forum = create_forum()
        cls.view = ForumView()
        cls.view.kwargs = {"pk": cls.forum.pk}
        cls.view.request = RequestFactory().get("/")
        cls.view.request.user = cls.user

    def test_excluded_announces_topics(self):
        TopicFactory(forum=self.forum, poster=self.user, type=Topic.TOPIC_ANNOUNCE)
        self.assertFalse(self.view.get_queryset())

    def test_exclude_not_approved_posts(self):
        TopicFactory(forum=self.forum, poster=self.user, approved=False)
        self.assertFalse(self.view.get_queryset())

    def test_pagination(self):
        self.assertEqual(10, self.view.paginate_by)

    def test_numqueries(self):
        poster = UserFactory()
        topics = TopicFactory.create_batch(10, forum=self.forum, poster=poster)
        _ = (PostFactory.create_batch(5, topic=topic, poster=poster) for topic in topics)

        UserForumPermissionFactory(
            permission=ForumPermission.objects.get(codename="can_see_forum"),
            forum=self.forum,
            user=self.user,
            has_perm=True,
        )
        UserForumPermissionFactory(
            permission=ForumPermission.objects.get(codename="can_read_forum"),
            forum=self.forum,
            user=self.user,
            has_perm=True,
        )

        url = reverse("forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug})

        self.client.force_login(self.user)

        # TODO fix vincentporte :
        # view to be optimized again soon
        with self.assertNumQueries(20):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_get_first_and_last_n_posts(self):
        n = 5

        topic = TopicFactory(forum=self.forum, poster=self.user)
        first_post = PostFactory(topic=topic, poster=self.user, content="first post")
        qs = self.view.get_queryset()
        self.assertEqual(qs.first().posts.all().count(), 1)
        self.assertEqual(qs.first().posts.first(), first_post)

        second_post = PostFactory(topic=topic, poster=self.user, content="second post")
        qs = self.view.get_queryset()
        self.assertEqual(qs.first().posts.all().count(), 2)
        self.assertEqual(qs.first().posts.first(), first_post)
        self.assertIn(second_post, qs.first().posts.all())

        PostFactory.create_batch(2 * n, topic=topic, poster=self.user)
        qs = self.view.get_queryset()
        self.assertGreater(topic.posts.count(), qs.first().posts.all().count())
        self.assertEqual(qs.first().posts.all().count(), n + 1)
        self.assertEqual(qs.first().posts.first(), first_post)
        self.assertNotIn(second_post, qs.first().posts.all())
        self.assertEqual(
            list(qs.first().posts.all().reverse().values("id")[:n]), list(topic.posts.all().reverse().values("id")[:n])
        )


class ForumViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.perm_handler = PermissionHandler()

        # Set up a top-level forum
        cls.forum = create_forum()

        # Set up a topic and some posts
        cls.topic = TopicFactory(forum=cls.forum, poster=cls.user)
        cls.post = PostFactory.create(topic=cls.topic, poster=cls.user)

        # Assign some permissions
        assign_perm("can_read_forum", cls.user, cls.forum)
        assign_perm("can_see_forum", cls.user, cls.forum)
        assign_perm("can_post_without_approval", cls.user, cls.forum)
        assign_perm("can_reply_to_topics", cls.user, cls.forum)

        cls.url = reverse("forum:forum", kwargs={"pk": cls.forum.pk, "slug": cls.forum.slug})

    def test_subscription_button_is_hidden(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:post_create",
                kwargs={
                    "forum_pk": self.forum.pk,
                    "forum_slug": self.forum.slug,
                    "topic_pk": self.topic.pk,
                    "topic_slug": self.topic.slug,
                },
            ),
        )
        self.assertNotContains(
            response,
            reverse(
                "forum_member:topic_subscribe",
                kwargs={
                    "pk": self.topic.pk,
                },
            ),
        )

    def test_topic_subject_is_not_hyperlink(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.subject)

        topic_url = reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.topic.pk,
                "slug": self.topic.slug,
            },
        )
        self.assertContains(response, f'<a href="{topic_url}post/create/')
        self.assertNotContains(response, f'<a href="{topic_url}"')

    def test_show_more_button_visibility(self):
        topic_url = reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.topic.pk,
                "slug": self.topic.slug,
            },
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'<a href="{topic_url}"')

        PostFactory.create_batch(10, topic=self.topic, poster=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<a href="{topic_url}"')

    def test_join_url_is_hidden(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            reverse(
                "members:join_forum_landing",
                kwargs={
                    "token": self.forum.invitation_token,
                },
            ),
        )

    def test_join_url_is_shown(self):
        assign_perm("can_approve_posts", self.user, self.forum)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            reverse(
                "members:join_forum_landing",
                kwargs={
                    "token": self.forum.invitation_token,
                },
            ),
        )


class ForumModelTest(TestCase):
    def test_invitation_token_is_unique(self):
        forum = create_forum()

        with self.assertRaises(IntegrityError):
            forum.id = None
            forum.save()
