from django.contrib.auth.models import AnonymousUser
from django.template.defaultfilters import truncatechars_html
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from faker import Faker
from machina.core.loading import get_class

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum
from lacommunaute.forum.views import ForumView
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.factories import CertifiedPostFactory
from lacommunaute.users.factories import UserFactory


faker = Faker()

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
        self.assertEqual(response.context_data["loadmoretopic_suffix"], "topicsinforum")

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
                "members:forum_profiles",
                kwargs={"pk": self.forum.pk, "slug": self.forum.slug},
            ),
        )

        # permission but no members group
        self.forum.members_group = None
        self.forum.save()
        response = self.client.get(self.url)
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

    def test_loadmoretopic_url_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["loadmoretopic_url"],
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={"forum_pk": self.forum.pk, "forum_slug": self.forum.slug},
            ),
        )

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
        with self.assertNumQueries(31):
            self.client.get(self.url)

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
        self.assertNotContains(response, truncatechars_html(post.content.rendered, 200))
        self.assertNotContains(response, topic_certified_post_url)
        self.assertNotContains(response, "Certifié par la Plateforme de l'Inclusion")

        # certify post
        CertifiedPostFactory(topic=self.topic, post=post, user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, truncatechars_html(post.content.rendered, 200))
        self.assertContains(response, topic_certified_post_url)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion")

    def test_loadmoretopic_url(self):
        TopicFactory.create_batch(9, with_post=True, forum=self.forum)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={"forum_pk": self.forum.pk, "forum_slug": self.forum.slug},
            )
            + "?page=2",
        )

        TopicFactory(with_post=True, forum=self.forum)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={"forum_pk": self.forum.pk, "forum_slug": self.forum.slug},
            )
            + "?page=2",
        )

        TopicFactory.create_batch(10, with_post=True, forum=self.forum)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={"forum_pk": self.forum.pk, "forum_slug": self.forum.slug},
            )
            + "?page=2",
        )

    def test_topic_has_tags(self):
        tag = f"tag_{faker.word()}"
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, tag)

        self.topic.tags.add(tag)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tag)

    def test_description_is_markdown_rendered(self):
        self.forum.description = "# title"
        self.forum.save()
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>title</h1>")

    def test_descendants_are_in_cards_if_forum_is_category_type(self):
        self.forum.type = Forum.FORUM_CAT
        self.forum.save()
        child_forum = ForumFactory(parent=self.forum)
        assign_perm("can_read_forum", self.user, child_forum)
        assign_perm("can_see_forum", self.user, child_forum)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="card-body')
        self.assertContains(response, child_forum.name)
        self.assertContains(
            response, reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
