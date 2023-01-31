from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from machina.core.loading import get_class

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.users.factories import UserFactory


assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class HomepageTest(TestCase):
    def test_home_page(self):
        url = reverse("forum_extension:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")


class StatistiquesPageTest(TestCase):
    def test_context_data(self):
        UserFactory()
        topic = TopicFactory(with_post=True, with_poll_vote=True)
        UpVoteFactory(post=topic.posts.first(), voter=topic.poster)

        url = reverse("pages:statistiques")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/statistiques.html")
        self.assertEqual(
            response.context_data["stats"],
            {
                "period": [timezone.now().strftime("%b %Y")],
                "pollvotes": [1],
                "upvotes": [1],
                "posts": [1],
                "topics": [1],
                "users": [2],
            },
        )
