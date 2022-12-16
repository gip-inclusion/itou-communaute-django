from django.test import TestCase
from django.urls import reverse
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.users.factories import UserFactory


Topic = get_model("forum_conversation", "Topic")
TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")

faker = Faker()


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

    def test_topic_is_marked_as_read_when_liking(self):
        # need an other unread topic to get TopicReadTrack
        # otherwise (when all topics are read), machina deletes
        # all TopicReadTrack and create/update ForumReadTrack
        TopicFactory(forum=self.topic.forum, poster=self.user)
        self.assertFalse(TopicReadTrack.objects.count())

        assign_perm("can_see_forum", self.user, self.topic.forum)
        assign_perm("can_read_forum", self.user, self.topic.forum)

        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, TopicReadTrack.objects.count())


class TopicContentView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.topic = TopicFactory(forum=create_forum(), poster=cls.user)
        cls.url = reverse(
            "forum_conversation_extension:showmore_topic",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )

    def test_cannot_read_topic(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_topic_doesnt_exist(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "forum_conversation_extension:showmore_posts",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk + 1,
                    "slug": self.topic.slug,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get_topic_content(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        post = PostFactory(topic=self.topic, poster=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.content)
        self.assertEqual(1, ForumReadTrack.objects.count())


class PostListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.topic = TopicFactory(forum=create_forum(), poster=cls.user)
        cls.url = reverse(
            "forum_conversation_extension:showmore_posts",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )

    def test_cannot_read_post(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_topic_doesnt_exist(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "forum_conversation_extension:showmore_posts",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk + 1,
                    "slug": self.topic.slug,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get_list_of_posts(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        posts = PostFactory.create_batch(3, topic=self.topic, poster=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, posts[0].content)  # original post content excluded
        self.assertContains(response, posts[1].content)
        self.assertContains(response, posts[2].content)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(1, ForumReadTrack.objects.count())


class PostFeedCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.topic = TopicFactory(forum=create_forum(), poster=cls.user)
        cls.url = reverse(
            "forum_conversation_extension:comment_topic",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )

    def test_get_method_unallowed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_cannot_post(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 403)

    def test_topic_doesnt_exist(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "forum_conversation_extension:comment_topic",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk + 1,
                    "slug": self.topic.slug,
                },
            ),
            data={},
        )

        self.assertEqual(response.status_code, 404)

    def test_form_is_invalid(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(self.url, data={})

        self.assertEqual(response.status_code, 500)

    def test_save_valid_post(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        PostFactory(topic=self.topic, poster=self.user)
        content = faker.text(max_nb_chars=20)
        self.client.force_login(self.user)

        response = self.client.post(self.url, data={"content": content})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, content)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(1, ForumReadTrack.objects.count())
