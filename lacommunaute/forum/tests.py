from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AnonymousUser, Group
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.conversation import create_topic
from machina.test.factories.forum import create_forum

from lacommunaute.forum.views import ForumView
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.forum_polls.factories import TopicPollFactory, TopicPollOptionFactory
from lacommunaute.users.factories import UserFactory


faker = Faker()

Topic = get_model("forum_conversation", "Topic")
Post = get_model("forum_conversation", "Post")
ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
remove_perm = get_class("forum_permission.shortcuts", "remove_perm")


class ForumViewQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.forum = create_forum()
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
        topic = TopicFactory(forum=self.forum, poster=self.user)
        topic.likers.add(self.user)
        topic.save()

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
        cls.user = UserFactory()
        cls.perm_handler = PermissionHandler()

        # Set up a top-level forum
        cls.forum = create_forum()

        # Set up a topic and some posts
        cls.topic = TopicFactory(forum=cls.forum, poster=cls.user)
        cls.post = PostFactory.create(topic=cls.topic, poster=cls.user)

        # Assign some permissions
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
                "forum_conversation_extension:comment_topic",
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
        self.assertContains(response, "Voir les 2 commentaires")

    def test_show_more_content(self):
        self.post.content = faker.paragraph(nb_sentences=100)
        self.post.save()
        topic_url = reverse(
            "forum_conversation_extension:showmore_topic",
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
        self.assertContains(response, f'hx-get="{topic_url}"')
        self.assertContains(response, "+ voir la suite")

    def test_join_url_is_hidden(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            reverse(
                "members:join_forum_form",
                kwargs={
                    "token": self.forum.invitation_token,
                },
            ),
        )

    def test_has_liked(self):
        topic = self.topic
        topic.likers.add(self.user)
        topic.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i>')
        self.assertContains(response, "<span>1 like</span>")

    def test_has_not_liked(self):
        topic = self.post.topic
        topic.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i>')
        self.assertContains(response, "<span>0 like</span>")

    def test_pluralized_likes(self):
        topic = self.post.topic
        topic.likers.add(UserFactory())
        topic.likers.add(UserFactory())
        topic.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i>')
        self.assertContains(response, "<span>2 likes</span>")

    def test_anonymous_like(self):
        assign_perm("can_read_forum", AnonymousUser(), self.post.topic.forum)
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
        poll_option = TopicPollOptionFactory(poll=TopicPollFactory(topic=self.topic))
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
        forum = create_forum()

        with self.assertRaises(IntegrityError):
            forum.id = None
            forum.save()

    def test_get_stats(self):

        poster = UserFactory()

        # create fake forum to ensure post and topic number is filter by forum
        forum_fake = create_forum()
        forum_fake.members_group = Group.objects.create(name="members_forum_fake")
        forum_fake.members_group.user_set.add(poster)
        forum_fake.members_group.user_set.add(UserFactory())
        topic = create_topic(forum=forum_fake, poster=poster)
        PostFactory(topic=topic, poster=poster)

        # create forum to test stats on it
        forum = create_forum()
        forum.members_group = Group.objects.create(name="members_forum")
        forum.members_group.user_set.add(poster)
        forum.members_group.user_set.add(UserFactory())
        forum.members_group.user_set.add(UserFactory())

        # create topics and posts
        now = timezone.now()
        for i in range(9):
            day = now - relativedelta(days=i - 1)

            for _ in range(2):
                # create topic and force topic created date (arg doesn't force created date)
                topic = create_topic(forum=forum, poster=poster)
                topic.created = day
                topic.save()

                for _ in range(3):
                    post = PostFactory(topic=topic, poster=poster)
                    post.created = day
                    post.save()

        # get forum stats for last 7 days
        stats = forum.get_stats(7)
        self.assertEqual(stats["days"][-1], str(now.date() + relativedelta(days=1)))
        self.assertEqual(stats["topics"][0], 4)
        self.assertEqual(stats["topics"][3], 10)
        self.assertEqual(stats["topics"][6], 16)
        self.assertEqual(stats["posts"][0], 12)
        self.assertEqual(stats["posts"][3], 30)
        self.assertEqual(stats["posts"][6], 48)
        self.assertEqual(stats["members"][-1], 3)

    def test_count_engaged_users(self):
        # first user posts, likes, votes
        topic = TopicFactory(with_post=True, with_like=True, with_vote=True)

        # second user posts
        PostFactory(topic=topic)

        # anonymous user posts
        PostFactory(topic=topic, anonymous=True)

        # post, like, vote in an other forum = ignored in count
        TopicFactory(with_post=True, with_like=True, with_vote=True)

        self.assertEqual(
            topic.forum.count_engaged_users,
            {"posters": 2, "likers": 1, "voters": 1, "authenticated_users": 2, "anonymous_posters": 1, "all_users": 3},
        )
