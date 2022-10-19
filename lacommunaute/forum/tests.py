from django.test import TestCase
from django.urls import reverse
from machina.core.db.models import get_model
from machina.test.factories.conversation import PostFactory, TopicFactory
from machina.test.factories.forum import create_forum
from machina.test.factories.permission import UserForumPermissionFactory

from lacommunaute.forum.views import ForumView
from lacommunaute.users.factories import DEFAULT_PASSWORD, UserFactory


Topic = get_model("forum_conversation", "Topic")
ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")


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
        with self.assertNumQueries(20):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
