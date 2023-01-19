from django.test import TestCase
from django.urls import reverse
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import UserFactory


ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")

faker = Faker()


class PostUpvoteViewTest(TestCase):
    """testing view dedicated in handling HTMX requests"""

    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        assign_perm("can_read_forum", cls.user, cls.topic.forum)
        cls.url = reverse("forum_upvote:upvote")
        cls.form_data = {"pk": cls.topic.pk, "post_pk": cls.topic.last_post.pk}

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_upvote_without_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 403)

    def test_upvote_downvote_post(self):
        self.client.force_login(self.user)
        post = PostFactory(topic=self.topic, poster=self.user)
        form_data = {"pk": self.topic.pk, "post_pk": post.pk}

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-fill" aria-hidden="true"></i>')
        self.assertContains(response, "1 vote")
        self.assertEqual(1, UpVote.objects.filter(voter_id=self.user.id, post_id=post.id).count())

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-line" aria-hidden="true"></i>')
        self.assertContains(response, "0 vote")
        self.assertEqual(0, UpVote.objects.filter(voter_id=self.user.id, post_id=post.id).count())

    def test_object_not_found(self):
        self.client.force_login(self.user)

        form_data = {"pk": 9999, "post_pk": self.topic.last_post.pk}

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(0, UpVote.objects.filter(voter_id=self.user.id, post_id=self.topic.last_post.id).count())

        form_data = {"pk": self.topic.pk, "post_pk": 9999}

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(0, UpVote.objects.filter(voter_id=self.user.id, post_id=self.topic.last_post.id).count())

    def test_topic_is_marked_as_read_when_upvoting(self):
        self.assertFalse(ForumReadTrack.objects.count())
        self.client.force_login(self.user)

        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ForumReadTrack.objects.count())
