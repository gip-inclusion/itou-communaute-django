from django.test import TestCase, override_settings
from django.urls import reverse
from machina.core.loading import get_class
from machina.test.factories.tracking import TopicReadTrackFactory

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forum_attachments.factories import AttachmentFactory
from lacommunaute.forum_conversation.forum_polls.factories import TopicPollFactory, TopicPollVoteFactory
from lacommunaute.users.factories import UserFactory


assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class ModeratorEngagementViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.url = reverse(
            "forum_extension:engagement",
            kwargs={"pk": cls.topic.forum.pk, "slug": cls.topic.forum.slug},
        )

    @override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
    def test_queryset(self):
        assign_perm("can_approve_posts", self.user, self.topic.forum)
        self.client.force_login(self.user)

        users = UserFactory.create_batch(3)

        # count views
        # count likes
        for user in users:
            TopicReadTrackFactory(topic=self.topic, user=user)
            self.topic.likers.add(user)
        self.topic.save()

        # count replies
        PostFactory(topic=self.topic, poster=self.user)

        # count attachments
        AttachmentFactory(post=self.topic.posts.first())

        # count votes
        poll = TopicPollFactory(topic=self.topic)
        TopicPollVoteFactory.create_batch(4, poll_option__poll=poll, voter=self.user)

        response = self.client.get(self.url)
        self.assertEqual(
            response.context["topics"].values("likes", "messages", "attached", "votes").first(),
            {"likes": 3, "messages": 2, "attached": 1, "votes": 4},
        )

        # exclued topic not approved
        not_approved_topic = TopicFactory(forum=self.topic.forum, poster=self.user, approved=False)
        response = self.client.get(self.url)
        self.assertNotIn(not_approved_topic, response.context["topics"])

        # order
        new_topic = TopicFactory(forum=self.topic.forum, poster=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["topics"].first(), new_topic)

    def test_context(self):
        assign_perm("can_approve_posts", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.context["forum"], self.topic.forum)
        topic = response.context["topics"][0]
        self.assertEqual(topic.id, self.topic.id)
        self.assertEqual(response.context["stats"], self.topic.forum.get_stats(7))

    def test_permission(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        assign_perm("can_approve_posts", self.user, self.topic.forum)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk,
                    "slug": self.topic.slug,
                },
            ),
        )

    def test_forum_doesnt_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "forum_extension:engagement",
                kwargs={"pk": 9999, "slug": self.topic.forum.slug},
            )
        )
        self.assertEqual(response.status_code, 404)


class FunnelViewTest(TestCase):
    def test_access(self):
        user = UserFactory()
        forum = ForumFactory()
        url = reverse(
            "forum_extension:funnel",
            kwargs={"pk": forum.pk, "slug": forum.slug},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        user.is_staff = True
        user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, forum.name)
