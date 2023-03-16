from django.test import TestCase
from django.urls import reverse
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_upvote.models import CertifiedPost, UpVote
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
        self.assertContains(response, '<i class="ri-star-fill" aria-hidden="true"></i><span class="ml-1">1</span>')
        self.assertEqual(1, UpVote.objects.filter(voter_id=self.user.id, post_id=post.id).count())

        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-line" aria-hidden="true"></i><span class="ml-1">0</span>')
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


class CertifiedPostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        assign_perm("can_read_forum", cls.user, cls.topic.forum)
        cls.url = reverse("forum_upvote:certify")
        cls.form_data = {"post_pk": cls.topic.last_post.pk}

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_instance_doesnt_exist(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={"post_pk": 9999})
        self.assertEqual(response.status_code, 404)

    def test_certify_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 403)

    def test_certify_with_permission(self):
        self.topic.forum.members_group.user_set.add(self.user)
        self.topic.forum.members_group.save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CertifiedPost.objects.count(), 1)
        certified_post = CertifiedPost.objects.first()
        self.assertEqual(certified_post.post, self.topic.last_post)
        self.assertEqual(certified_post.user, self.user)
        self.assertEqual(certified_post.topic, self.topic)
        self.assertEqual(ForumReadTrack.objects.count(), 1)

    def test_uncertify_with_permission(self):
        self.topic.forum.members_group.user_set.add(self.user)
        self.topic.forum.members_group.save()
        CertifiedPost(topic=self.topic, post=self.topic.last_post, user=self.user).save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CertifiedPost.objects.count(), 0)
        self.assertEqual(ForumReadTrack.objects.count(), 1)

    def test_rendered_content(self):
        self.topic.forum.members_group.user_set.add(self.user)
        self.topic.forum.members_group.save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<div id="showmorepostsarea{self.topic.pk}">')
        self.assertTemplateUsed(response, "forum_conversation/partials/posts_list.html")
