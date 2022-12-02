from django.test import TestCase
from django.urls import reverse
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.users.factories import UserFactory


Topic = get_model("forum_conversation", "Topic")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class TopicLikeViewTest(TestCase):
    """testing view dedicated in handling HTMX requests"""

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.topic = TopicFactory(forum=create_forum(), poster=cls.user)
        cls.url = reverse(
            "forum_conversation_extension:like_topic",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_anonymous(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        # vincentporte : response contains redirection, how to handle it through HTMX Post Request ?
        self.assertEqual(response.url, reverse("inclusion_connect:authorize") + "?next=" + self.url)

    def test_post_without_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_like_unlike_topic(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i>')
        self.assertContains(response, "<span>1 like</span>")

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i>')
        self.assertContains(response, "<span>0 like</span>")

    def test_post_topic_not_found(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        bad_slug_url = reverse(
            "forum_conversation_extension:like_topic",
            kwargs={
                "forum_pk": self.topic.forum.pk,
                "forum_slug": self.topic.forum.slug,
                "pk": 9999999,
                "slug": self.topic.slug,
            },
        )

        self.assertEqual(0, Topic.objects.get(id=self.topic.pk).likers.count())

        response = self.client.post(bad_slug_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(0, Topic.objects.get(id=self.topic.pk).likers.count())

    def test_post_pluralized_likes(self):
        topic = self.topic
        topic.likers.add(UserFactory())
        topic.likers.add(UserFactory())
        topic.save()

        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i>')
        self.assertContains(response, "<span>3 likes</span>")
