from django.test import TestCase
from django.urls import reverse

from lacommunaute.forum_member.factories import ForumProfileFactory
from lacommunaute.forum_member.models import ForumProfile


class ForumProfileListViewTest(TestCase):
    def test_ForumProfileListView(self):
        forum_profiles = ForumProfileFactory.create_batch(2)
        response = self.client.get(reverse("members:profiles"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["forum_profiles"]), ForumProfile.objects.count()
        )

        for forum_profile in forum_profiles:
            with self.subTest(forum_profile=forum_profile):
                self.assertContains(response, forum_profile.user.first_name)
                self.assertContains(
                    response,
                    # legacy machina reversed url
                    reverse(
                        "forum_member:profile", kwargs={"pk": forum_profile.user_id}
                    ),
                )
