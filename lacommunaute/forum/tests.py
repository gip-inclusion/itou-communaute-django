from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.views import ForumView
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.forum_polls.factories import TopicPollVoteFactory
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.users.factories import UserFactory


faker = Faker()

ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
remove_perm = get_class("forum_permission.shortcuts", "remove_perm")


class ForumViewQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.forum = ForumFactory()
        cls.view = ForumView()
        cls.view.kwargs = {"pk": cls.forum.pk}
        cls.view.request = RequestFactory().get("/")
        cls.view.request.user = cls.user

    def test_excluded_announces_topics(self):
        TopicFactory(forum=self.forum, poster=self.user, type=Topic.TOPIC_ANNOUNCE)
        self.assertFalse(self.view.get_queryset())

    def test_exclude_not_approved_posts(self):
        TopicFactory(forum=self.forum, poster=self.user, approved=False)
        self.assertFalse(self.view.get_queryset())

    def test_ordering_topics_on_last_post(self):
        old_topic = TopicFactory(forum=self.forum, poster=self.user)
        new_topic = TopicFactory(forum=self.forum, poster=self.user)

        PostFactory(topic=old_topic, poster=self.user)
        PostFactory(topic=new_topic, poster=self.user)

        qs = self.view.get_queryset()
        self.assertEqual(qs.first(), new_topic)
        self.assertEqual(qs.last(), old_topic)

        PostFactory(topic=old_topic, poster=self.user)
        self.assertEqual(qs.first(), old_topic)
        self.assertEqual(qs.last(), new_topic)

    def test_pagination(self):
        self.assertEqual(10, self.view.paginate_by)

    def test_has_liked(self):
        TopicFactory(forum=self.forum, poster=self.user, with_like=True)

        first_topic = self.view.get_queryset().first()
        self.assertEqual(first_topic.likes, 1)
        self.assertTrue(first_topic.has_liked)

    def test_has_not_liked(self):
        TopicFactory(forum=self.forum, poster=self.user)

        first_topic = self.view.get_queryset().first()
        self.assertEqual(first_topic.likes, 0)
        self.assertFalse(first_topic.has_liked)


class ForumViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.forum = cls.topic.forum

        # Assign some permissions
        cls.perm_handler = PermissionHandler()
        assign_perm("can_read_forum", cls.user, cls.forum)
        assign_perm("can_see_forum", cls.user, cls.forum)
        assign_perm("can_post_without_approval", cls.user, cls.forum)
        assign_perm("can_reply_to_topics", cls.user, cls.forum)

        cls.url = reverse("forum:forum", kwargs={"pk": cls.forum.pk, "slug": cls.forum.slug})

    def test_subscription_button_is_hidden(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation_extension:post_create",
                kwargs={
                    "forum_pk": self.forum.pk,
                    "forum_slug": self.forum.slug,
                    "pk": self.topic.pk,
                    "slug": self.topic.slug,
                },
            ),
        )
        self.assertNotContains(
            response,
            reverse(
                "forum_member:topic_subscribe",
                kwargs={
                    "pk": self.topic.pk,
                },
            ),
        )

    def test_show_comments(self):
        topic_url = reverse(
            "forum_conversation_extension:showmore_posts",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.topic.pk,
                "slug": self.topic.slug,
            },
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'<a href="{topic_url}"')

        PostFactory.create_batch(2, topic=self.topic, poster=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'hx-get="{topic_url}"')
        self.assertContains(response, "Voir les 2 autres réponses")

    def test_show_more_content(self):
        topic = TopicFactory(
            with_post=True, poster=self.user, forum=self.forum, post__content=faker.paragraph(nb_sentences=100)
        )
        topic_url = reverse(
            "forum_conversation_extension:showmore_topic",
            kwargs={
                "forum_pk": topic.forum.pk,
                "forum_slug": topic.forum.slug,
                "pk": topic.pk,
                "slug": topic.slug,
            },
        )
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'hx-get="{topic_url}"')
        self.assertContains(response, "+ voir la suite")

    def test_has_liked(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, with_like=True)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i>')
        self.assertContains(response, "<span>1 J'aime</span>")

    def test_has_not_liked(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i>')
        self.assertContains(response, "<span>0 J'aime</span>")

    def test_anonymous_like(self):
        assign_perm("can_read_forum", AnonymousUser(), self.topic.forum)
        params = {"next_url": self.url}
        url = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"

        response = self.client.get(self.url)
        self.assertContains(response, url)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(response, url)

    def test_moderator_links(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            reverse(
                "forum_extension:engagement",
                kwargs={"pk": self.forum.pk, "slug": self.forum.slug},
            ),
        )
        self.assertNotContains(
            response,
            reverse(
                "members:forum_profiles",
                kwargs={"pk": self.forum.pk, "slug": self.forum.slug},
            ),
        )

        assign_perm("can_approve_posts", self.user, self.forum)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            reverse(
                "forum_extension:engagement",
                kwargs={"pk": self.forum.pk, "slug": self.forum.slug},
            ),
        )
        self.assertContains(
            response,
            reverse(
                "members:forum_profiles",
                kwargs={"pk": self.forum.pk, "slug": self.forum.slug},
            ),
        )

    def test_poll_form(self):
        topic = TopicFactory(forum=self.forum, poster=self.user, with_post=True, with_poll_vote=True)
        poll_option = topic.poll.options.first()
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, poll_option.poll.question)
        self.assertContains(response, poll_option.text)

    def test_postform_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context_data["form"], PostForm)
        self.assertContains(response, f'id="collapsePost{self.topic.pk}')

    def test_cannot_submit_post(self):
        user = UserFactory()
        assign_perm("can_read_forum", user, self.forum)
        assign_perm("can_see_forum", user, self.forum)
        remove_perm("can_reply_to_topics", user, self.forum)
        self.client.force_login(user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'id="collapsePost{self.topic.pk}')


class ForumModelTest(TestCase):
    def test_invitation_token_is_unique(self):
        forum = ForumFactory()

        with self.assertRaises(IntegrityError):
            forum.id = None
            forum.save()

    def test_get_stats(self):

        forum = ForumFactory()
        topic = TopicFactory(forum=forum, with_post=True, with_poll_vote=True)
        UpVoteFactory(post=topic.posts.first(), voter=topic.poster)

        # create old instance to ensure they are filtered
        fifteen_days_ago = timezone.now() - relativedelta(days=15)
        old_topic = TopicFactory(forum=forum)
        old_topic.created = fifteen_days_ago
        old_topic.save()
        old_post = PostFactory(topic=old_topic, poster=old_topic.poster)
        old_post.created = fifteen_days_ago
        old_post.save()
        old_pollvote = TopicPollVoteFactory(voter=old_topic.poster, poll_option__poll__topic=old_topic)
        old_pollvote.timestamp = fifteen_days_ago
        old_pollvote.save()
        old_upvote = UpVoteFactory(post=old_topic.posts.first(), voter=old_topic.poster)
        old_upvote.created_at = fifteen_days_ago
        old_upvote.save()

        # create fake forum to ensure post, topic, etc… number is filter by forum
        fake_forum = ForumFactory()
        fake_topic = TopicFactory(forum=fake_forum, with_post=True, with_poll_vote=True)
        UpVoteFactory(post=fake_topic.posts.first(), voter=fake_topic.poster)

        self.assertEqual(
            forum.get_stats(1),
            {
                "period": [timezone.now().strftime("%Y-%W")],
                "pollvotes": [1],
                "upvotes": [1],
                "posts": [1],
                "topics": [1],
            },
        )

    def test_count_engaged_users(self):
        # first user posts, likes, votes
        topic = TopicFactory(with_post=True, with_like=True, with_poll_vote=True)

        # second user posts
        PostFactory(topic=topic, with_upvote=True)

        # anonymous user posts
        PostFactory(topic=topic, anonymous=True)

        # post, like, vote in an other forum = ignored in count
        TopicFactory(with_post=True, with_like=True, with_poll_vote=True)

        self.assertEqual(
            topic.forum.count_engaged_users,
            {
                "posters": 2,
                "likers": 1,
                "voters": 1,
                "upvoters": 1,
                "authenticated_users": 2,
                "anonymous_posters": 1,
                "all_users": 3,
            },
        )
