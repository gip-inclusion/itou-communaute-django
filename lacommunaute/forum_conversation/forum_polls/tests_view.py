from django.test import TestCase
from django.urls import reverse
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.polls import TopicPollFactory, TopicPollOptionFactory

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forum_polls.models import TopicPollVote
from lacommunaute.users.factories import UserFactory


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")

TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")


class TopicPollVoteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.perm_handler = PermissionHandler()
        cls.topic = TopicFactory(poster=cls.user)
        cls.forum = cls.topic.forum
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

    def test_topic_is_marked_as_read_when_voting(self):
        # need an other unread topic to get TopicReadTrack
        # otherwise (when all topics are read), machina deletes
        # all TopicReadTrack and create/update ForumReadTrack
        TopicFactory(forum=self.forum, poster=self.user)
        self.assertEqual(TopicReadTrack.objects.count(), 0)

        assign_perm("can_vote_in_polls", self.user, self.forum)

        self.client.force_login(self.user)

        post_data = {
            "options": [
                self.poll_option.pk,
            ],
        }
        response = self.client.post(self.url, post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, TopicReadTrack.objects.count())
