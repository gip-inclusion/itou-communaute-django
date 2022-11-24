from django.test import TestCase, override_settings
from django.urls import reverse
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.attachments import AttachmentFactory
from machina.test.factories.conversation import create_topic
from machina.test.factories.forum import create_forum
from machina.test.factories.tracking import TopicReadTrackFactory

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
Topic = get_model("forum_conversation", "Topic")


class ModeratorEngagementViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        # cls.perm_handler = PermissionHandler()
        cls.post = PostFactory(topic=create_topic(forum=create_forum(), poster=cls.user), poster=cls.user)
        cls.url = reverse(
            "forum_extension:engagement",
            kwargs={"pk": cls.post.topic.forum.pk, "slug": cls.post.topic.forum.slug},
        )

    @override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
    def test_queryset(self):
        assign_perm("can_approve_posts", self.user, self.post.topic.forum)
        self.client.force_login(self.user)

        users = UserFactory.create_batch(3)

        # count views
        # count likes
        for user in users:
            TopicReadTrackFactory(topic=self.post.topic, user=user)
            self.post.topic.likers.add(user)
        self.post.topic.save()

        # count replies
        PostFactory(topic=self.post.topic, poster=self.user)

        # count attachments
        AttachmentFactory(post=self.post)

        response = self.client.get(self.url)
        self.assertEqual(
            response.context["topics"].values("likes", "views", "replies", "attached").first(),
            {"likes": 3, "views": 3, "replies": 2, "attached": 1},
        )

        # exclued topic not approved
        not_approved_topic = TopicFactory(forum=self.post.topic.forum, poster=self.user, approved=False)
        response = self.client.get(self.url)
        self.assertNotIn(not_approved_topic, response.context["topics"])

        # order
        new_topic = TopicFactory(forum=self.post.topic.forum, poster=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["topics"].first(), new_topic)

    def test_context(self):
        assign_perm("can_approve_posts", self.user, self.post.topic.forum)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["forum"], self.post.topic.forum)
        topic = response.context["topics"][0]
        self.assertEqual(topic.id, self.post.topic.id)

    def test_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        assign_perm("can_approve_posts", self.user, self.post.topic.forum)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_pk": self.post.topic.forum.pk,
                    "forum_slug": self.post.topic.forum.slug,
                    "pk": self.post.topic.pk,
                    "slug": self.post.topic.slug,
                },
            ),
        )

    def test_forum_doesnt_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "forum_extension:engagement",
                kwargs={"pk": 9999, "slug": self.post.topic.forum.slug},
            )
        )
        self.assertEqual(response.status_code, 404)
