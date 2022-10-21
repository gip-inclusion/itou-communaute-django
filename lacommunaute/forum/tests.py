from django.test import TestCase
from django.urls import reverse
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.conversation import PostFactory, TopicFactory, create_topic
from machina.test.factories.forum import create_forum
from machina.test.factories.permission import UserForumPermissionFactory

from lacommunaute.forum.views import ForumView
from lacommunaute.users.factories import DEFAULT_PASSWORD, UserFactory


Topic = get_model("forum_conversation", "Topic")
ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class ForumViewQuerysetTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.forum = create_forum()

    def test_excluded_announces_topics(self):
        TopicFactory(forum=self.forum, poster=self.user, type=Topic.TOPIC_ANNOUNCE)
        view = ForumView()
        view.kwargs = {"pk": self.forum.pk}
        self.assertFalse(view.get_queryset())

    def test_exclude_not_approved_posts(self):
        TopicFactory(
            forum=self.forum, poster=self.user, approved=False, type=Topic.TOPIC_POST
        )
        view = ForumView()
        view.kwargs = {"pk": self.forum.pk}
        self.assertFalse(view.get_queryset())

    def test_pagination(self):
        view = ForumView()
        self.assertEquals(10, view.paginate_by)

    def test_numqueries(self):
        poster = UserFactory()
        topics = TopicFactory.create_batch(
            10, forum=self.forum, poster=poster, type=Topic.TOPIC_POST
        )
        _ = (
            PostFactory.create_batch(5, topic=topic, poster=poster) for topic in topics
        )

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

        url = reverse(
            "forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}
        )

        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)

        # todo fix vincentporte :
        # assumed duplicated queries in ForumView()
        # view to be optimized again soon


class ForumViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.perm_handler = PermissionHandler()

        # Set up a top-level forum
        self.forum = create_forum()

        # Set up a topic and some posts
        self.topic = create_topic(forum=self.forum, poster=self.user)
        self.post = PostFactory.create(topic=self.topic, poster=self.user)

        # Assign some permissions
        assign_perm("can_read_forum", self.user, self.forum)
        assign_perm("can_see_forum", self.user, self.forum)
        assign_perm("can_post_without_approval", self.user, self.forum)
        assign_perm("can_reply_to_topics", self.user, self.forum)

    def test_subscription_button_is_hidden(self):
        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        url = reverse(
            "forum:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}
        )

        self.client.login(username=self.user.username, password=DEFAULT_PASSWORD)
        response = self.client.get(url)

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


        self.assertEqual(response.status_code, 200)
