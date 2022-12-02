from django.test import TestCase
from django.urls import reverse
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.forum import create_forum
from machina.test.factories.polls import TopicPollFactory, TopicPollOptionFactory

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
TopicPollVote = get_model("forum_polls", "TopicPollVote")


class TopicPollVoteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.perm_handler = PermissionHandler()
        cls.forum = create_forum()
        cls.topic = TopicFactory(forum=cls.forum, poster=cls.user)
        cls.post = PostFactory.create(topic=cls.topic, poster=cls.user)
        cls.poll_option = TopicPollOptionFactory(poll=TopicPollFactory(topic=cls.topic))
        cls.url = reverse(
            "forum_polls_extension:topic_poll_vote",
            kwargs={"forum_pk": cls.forum.pk, "forum_slug": cls.forum.slug, "pk": cls.poll_option.poll.pk},
        )

    def test_can_vote_in_polls(self):
        assign_perm("can_vote_in_polls", self.user, self.forum)

        self.client.force_login(self.user)

        post_data = {
            "options": [
                self.poll_option.pk,
            ],
        }
        response = self.client.post(self.url, post_data, follow=True)
        # Check
        self.assertEqual(response.status_code, 200)
        votes = TopicPollVote.objects.filter(voter=self.user)
        self.assertEqual(votes.count(), 1)
        self.assertEqual(votes[0].poll_option, self.poll_option)

    def test_cannot_vote_in_polls(self):
        self.client.force_login(self.user)

        post_data = {
            "options": [
                self.poll_option.pk,
            ],
        }
        response = self.client.post(self.url, post_data, follow=True)
        # Check
        self.assertEqual(response.status_code, 403)
        votes = TopicPollVote.objects.filter(voter=self.user)
        self.assertEqual(votes.count(), 0)
