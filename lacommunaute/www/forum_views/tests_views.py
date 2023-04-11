from django.contrib.auth.models import AnonymousUser, Group
from django.template.defaultfilters import truncatechars
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.http import urlencode
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class
from machina.test.factories.tracking import TopicReadTrackFactory

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.forum_attachments.factories import AttachmentFactory
from lacommunaute.forum_conversation.forum_polls.factories import TopicPollFactory, TopicPollVoteFactory
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.factories import CertifiedPostFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.www.forum_views.views import ForumView


faker = Faker()

PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
remove_perm = get_class("forum_permission.shortcuts", "remove_perm")

ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
GroupForumPermission = get_model("forum_permission", "GroupForumPermission")


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

        cls.url = reverse("forum_extension:forum", kwargs={"pk": cls.forum.pk, "slug": cls.forum.slug})

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
        self.assertContains(response, "Voir les 2 réponses")

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
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

    def test_has_not_liked(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">0</span>')

    def test_has_liked_TOPIC_ANNOUNCE(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, with_like=True, type=Topic.TOPIC_ANNOUNCE)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

    def test_has_not_liked_TOPIC_ANNOUNCE(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, type=Topic.TOPIC_ANNOUNCE)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">0</span>')

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

        # no permission
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

        # permission
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

        # permission but no members group
        self.forum.members_group = None
        self.forum.save()
        response = self.client.get(self.url)
        self.assertContains(
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

    def test_queries(self):
        TopicFactory.create_batch(20, with_post=True)
        self.client.force_login(self.user)
        with self.assertNumQueries(26):
            self.client.get(self.url)

    def test_param_new_in_request(self):
        topic_with_2_posts = TopicFactory(with_post=True, forum=self.forum)
        topic_is_locked = TopicFactory(with_post=True, forum=self.forum, status=Topic.TOPIC_LOCKED)
        PostFactory(topic=topic_with_2_posts)
        self.client.force_login(self.user)

        response = self.client.get(self.url + "?new=1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.topic, response.context_data["topics"])
        self.assertNotIn(topic_with_2_posts, response.context_data["topics"])
        self.assertNotIn(topic_is_locked, response.context_data["topics"])

    # test CertifiedPost display
    def test_certified_post_display(self):
        topic_certified_post_url = reverse(
            "forum_conversation_extension:showmore_certified",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.topic.pk,
                "slug": self.topic.slug,
            },
        )
        self.client.force_login(self.user)

        # create a post which is not certified
        post = PostFactory(topic=self.topic, poster=self.user, content=faker.paragraph(nb_sentences=100))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, truncatechars(post.content.rendered, 200))
        self.assertNotContains(response, topic_certified_post_url)
        self.assertNotContains(response, "Certifié par la Plateforme de l'Inclusion")

        # certify post
        CertifiedPostFactory(topic=self.topic, post=post, user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, truncatechars(post.content.rendered, 200))
        self.assertContains(response, topic_certified_post_url)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion")


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


class IndexViewTest(TestCase):
    def setUp(self):
        self.url = reverse("forum_extension:home")
        self.forum = ForumFactory()
        self.user = UserFactory()

    def test_forum_is_not_visible_without_perms(self):
        response = self.client.get(reverse("forum_extension:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.forum.name)

    def test_forum_is_visible_with_authenticated_perms(self):
        assign_perm("can_see_forum", self.user, self.forum)
        assign_perm("can_read_forum", self.user, self.forum)
        self.client.force_login(self.user)
        response = self.client.get(reverse("forum_extension:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.forum.name)

    def test_forum_is_visible_with_anonymous_perms(self):
        assign_perm("can_see_forum", AnonymousUser(), self.forum)
        assign_perm("can_read_forum", AnonymousUser(), self.forum)
        response = self.client.get(reverse("forum_extension:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.forum.name)

    def test_form_is_in_context(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context_data["form"], PostForm)

    def test_unaswered_topics_visibility(self):
        unanswered_private_topic = TopicFactory(forum=ForumFactory(is_private=True), with_post=True)
        unanswered_public_topic = TopicFactory(forum=ForumFactory(is_private=False), with_post=True)

        response = self.client.get(self.url)

        self.assertNotIn(unanswered_private_topic, response.context["topics"])
        self.assertIn(unanswered_public_topic, response.context["topics"])

    def test_parameters_in_url(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="nav-link" id="pending-topics-tab"')
        self.assertContains(response, 'class="tab-pane fade" id="pending-topics"')
        self.assertContains(response, 'class="nav-link active" id="forums_tab"')
        self.assertContains(response, 'class="tab-pane fade show active" id="forums"')

        url = self.url + "?new=1"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="nav-link active" id="pending-topics-tab"')
        self.assertContains(response, 'class="tab-pane fade show active" id="pending-topics"')
        self.assertContains(response, 'class="nav-link" id="forums_tab"')
        self.assertContains(response, 'class="tab-pane fade" id="forums"')

    def test_has_liked(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, with_like=True)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')


class CreateForumView(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = reverse("forum_extension:create")

    def test_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        name = faker.name()

        response = self.client.post(
            self.url,
            {
                "name": name,
                "description": "Test",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("forum_extension:home"))

        self.assertEqual(Forum.objects.count(), 1)
        self.assertEqual(Forum.objects.first().name, name)

        self.assertEqual(
            UserForumPermission.objects.filter(anonymous_user=True).count(), ForumPermission.objects.count()
        )
        self.assertEqual(
            UserForumPermission.objects.filter(authenticated_user=True).count(), ForumPermission.objects.count()
        )

        self.assertEqual(Group.objects.filter(name=f"{name} moderators").count(), 1)
        self.assertEqual(
            GroupForumPermission.objects.filter(group=Group.objects.filter(name=f"{name} moderators").first()).count(),
            ForumPermission.objects.count(),
        )
