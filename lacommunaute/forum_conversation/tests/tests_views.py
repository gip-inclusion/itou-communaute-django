from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class
from taggit.models import Tag

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.enums import Filters
from lacommunaute.forum_conversation.factories import CertifiedPostFactory, PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.views import PostDeleteView, TopicCreateView
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.notification.factories import BouncedEmailFactory
from lacommunaute.users.factories import UserFactory


faker = Faker()

PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class TopicCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poster = UserFactory()
        cls.forum = ForumFactory(with_public_perms=True)
        cls.url = reverse(
            "forum_conversation:topic_create",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
            },
        )

        cls.post_data = {"subject": faker.text(max_nb_chars=10), "content": faker.text(max_nb_chars=30)}

    def test_get_success_url(self):
        view = TopicCreateView()
        view.request = RequestFactory().get("/")
        topic = TopicFactory(with_post=True)
        view.forum_post = topic.first_post
        view.forum_post.topic = topic

        view.forum_post.approved = False
        success_url = view.get_success_url()

        self.assertEqual(
            success_url,
            reverse(
                "forum_extension:forum",
                kwargs={"slug": topic.forum.slug, "pk": topic.forum.pk},
            ),
        )

        view.forum_post.approved = True
        success_url = view.get_success_url()

        self.assertEqual(
            success_url,
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_slug": topic.forum.slug,
                    "forum_pk": topic.forum.pk,
                    "pk": topic.pk,
                    "slug": topic.slug,
                },
            ),
        )

    def test_delete_button_is_hidden(self, *args):
        self.client.force_login(self.poster)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, '/post/delete/" title="Supprimer" role="button" class="btn btn-outline-danger">Supprimer</a>'
        )

    def test_topic_poster_is_added_to_likers_list(self, *args):
        self.client.force_login(self.poster)

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Topic.objects.count())
        self.assertEqual(1, Topic.objects.first().likers.count())

    def test_topic_create_as_anonymous_user(self, *args):
        self.post_data["username"] = faker.email()

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Topic.objects.count())
        topic = Topic.objects.first()
        self.assertEqual(self.post_data["subject"], topic.subject)
        self.assertEqual(self.post_data["subject"], topic.first_post.subject)
        self.assertEqual(self.post_data["content"], topic.first_post.content.raw)
        self.assertEqual(self.post_data["username"], topic.first_post.username)
        self.assertEqual(0, topic.likers.count())
        self.assertTrue(topic.approved)
        self.assertTrue(topic.first_post.approved)

    def test_topic_create_as_unapproved_anonymous_user(self, *args):
        self.post_data["username"] = faker.email()
        BouncedEmailFactory(email=self.post_data["username"])

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Topic.objects.count())
        topic = Topic.objects.first()
        self.assertFalse(topic.approved)
        self.assertFalse(topic.first_post.approved)

    def test_topic_create_as_authenticated_user(self, *args):
        self.client.force_login(self.poster)

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Topic.objects.first().approved)
        self.assertTrue(Topic.objects.first().posts.first().approved)

    def test_tags_checkbox_are_displayed(self, *args):
        Tag.objects.bulk_create([Tag(name=f"tag_x{i}", slug=f"tag_x{i}") for i in range(2)])
        self.client.force_login(self.poster)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Tag.objects.first().name)
        self.assertContains(response, Tag.objects.last().name)

    def test_checked_tags_are_saved(self, *args):
        Tag.objects.bulk_create([Tag(name=f"tag_y{i}", slug=f"tag_y{i}") for i in range(3)])
        self.client.force_login(self.poster)
        post_data = {
            "subject": faker.text(max_nb_chars=5),
            "content": faker.text(max_nb_chars=5),
            "tags": [Tag.objects.first().pk, Tag.objects.last().pk],
        }

        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Topic.objects.count())
        topic = Topic.objects.first()
        self.assertEqual(2, topic.tags.count())
        self.assertEqual(list(topic.tags.all()), [Tag.objects.first(), Tag.objects.last()])


class TopicUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.forum = ForumFactory(with_public_perms=True)
        cls.topic = TopicFactory(with_post=True, forum=cls.forum)
        cls.poster = cls.topic.poster
        cls.url = reverse(
            "forum_conversation:topic_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "slug": cls.topic.slug,
                "pk": cls.topic.pk,
            },
        )

    def test_delete_post_button_is_shown(self):
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation:post_delete",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "topic_slug": self.topic.slug,
                    "topic_pk": self.topic.pk,
                    "pk": self.topic.posts.first().pk,
                },
            ),
        )

    def test_topic_is_marked_as_read_when_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        self.client.force_login(self.poster)

        post_data = {"subject": "s", "content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ForumReadTrack.objects.count())

    def test_selected_tags_are_checked(self):
        self.client.force_login(self.poster)

        tag = Tag.objects.create(name=faker.word())

        linked_tag = Tag.objects.create(name=faker.word())
        self.topic.tags.add(linked_tag)
        self.topic.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        checked_box = f'type="checkbox" name="tags" value="{linked_tag.id}" checked="">'
        self.assertContains(response, checked_box)
        not_checked_box = f'type="checkbox" name="tags" value="{tag.id}">'
        self.assertContains(response, not_checked_box)


class PostCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.url = reverse(
            "forum_conversation:post_create",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "topic_slug": cls.topic.slug,
                "topic_pk": cls.topic.pk,
            },
        )

    def test_machina_route_forbidden(self):
        self.client.force_login(self.poster)

        post_data = {"content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 403)


class PostUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.forum = ForumFactory(with_public_perms=True)
        cls.topic = TopicFactory(with_post=True, forum=cls.forum)
        cls.post = PostFactory(topic=cls.topic)
        cls.poster = cls.post.poster
        cls.kwargs = {
            "forum_slug": cls.forum.slug,
            "forum_pk": cls.forum.pk,
            "topic_slug": cls.topic.slug,
            "topic_pk": cls.topic.pk,
            "pk": cls.post.pk,
        }
        cls.url = reverse("forum_conversation:post_update", kwargs=cls.kwargs)
        cls.post_data = {"content": faker.text(max_nb_chars=20)}

    def test_delete_post_button_is_visible(self, *args):
        self.client.force_login(self.poster)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("forum_conversation:post_delete", kwargs=self.kwargs))

    def test_update_post_as_authenticated_user(self, *args):
        self.client.force_login(self.poster)

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content.raw, self.post_data["content"])
        self.assertIsNone(self.post.username)
        self.assertTrue(self.post.approved)

    @patch("machina.apps.forum_conversation.views.PostUpdateView.perform_permissions_check", return_value=True)
    def test_update_post_as_anonymous_user(self, *args):
        self.post_data["username"] = faker.email()
        url = reverse("forum_conversation:post_update", kwargs=self.kwargs)

        response = self.client.post(
            url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.username, self.post_data["username"])
        self.assertTrue(self.post.approved)

        BouncedEmailFactory(email=self.post_data["username"])

        response = self.client.post(
            url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertFalse(self.post.approved)


class PostDeleteViewTest(TestCase):
    def test_redirection(self):
        topic = TopicFactory(with_post=True)

        factory = RequestFactory()
        request = factory.get("/")
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        view = PostDeleteView()
        view.object = topic.posts.first()
        view.request = request
        self.assertEqual(
            view.get_success_url(),
            reverse("forum_extension:forum", kwargs={"pk": topic.forum.pk, "slug": topic.forum.slug}),
        )
        msgs = get_messages(request)
        self.assertTrue(view.success_message, msgs._queued_messages[0].message)


class TopicViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.perm_handler = PermissionHandler()
        assign_perm("can_read_forum", cls.poster, cls.topic.forum)
        assign_perm("can_see_forum", cls.poster, cls.topic.forum)
        cls.kwargs = {
            "forum_pk": cls.topic.forum.pk,
            "forum_slug": cls.topic.forum.slug,
            "pk": cls.topic.pk,
            "slug": cls.topic.slug,
        }
        cls.url = reverse("forum_conversation:topic", kwargs=cls.kwargs)

    def test_has_liked(self):
        self.topic.likers.add(self.poster)
        self.topic.save()

        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

    def test_has_not_liked(self):
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">0</span>')

    def test_pluralized_likes(self):
        self.topic.likers.add(UserFactory())
        self.topic.likers.add(UserFactory())
        self.topic.save()

        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">2</span>')

    def test_anonymous_like(self):
        assign_perm("can_read_forum", AnonymousUser(), self.topic.forum)
        params = {"next_url": self.url}
        url = f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"

        response = self.client.get(self.url)
        self.assertContains(response, url)

        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertNotContains(response, url)

    def test_post_has_no_upvote(self):
        PostFactory(topic=self.topic, poster=self.poster)
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-line" aria-hidden="true"></i><span class="ml-1">0</span>')

    def test_post_has_upvote_by_user(self):
        PostFactory(topic=self.topic, poster=self.poster)
        UpVoteFactory(post=self.topic.last_post, voter=self.poster)
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

    def test_certified_post_is_highlighted(self):
        post = PostFactory(topic=self.topic, poster=self.poster)
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Certifié par la Plateforme de l'Inclusion")

        CertifiedPostFactory(topic=self.topic, post=post, user=self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion")

    def test_has_tags(self):
        tag = f"tag_{faker.word()}"
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, tag)

        self.topic.tags.add(tag)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, tag)

    def test_edit_link_is_visible(self):
        self.client.force_login(self.poster)
        assign_perm("can_edit_own_posts", self.poster, self.forum)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("forum_conversation:topic_update", kwargs=self.kwargs))

    def test_numqueries(self):
        PostFactory.create_batch(10, topic=self.topic, poster=self.poster)
        UpVoteFactory(post=self.topic.last_post, voter=UserFactory())
        CertifiedPostFactory(topic=self.topic, post=self.topic.last_post, user=UserFactory())
        self.client.force_login(self.poster)

        # note vincentporte : to be optimized
        with self.assertNumQueries(44):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TopicListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("forum_conversation_extension:topics")
        cls.forum = ForumFactory(with_public_perms=True)
        cls.topic = TopicFactory(with_post=True, with_like=True, forum=cls.forum)
        cls.user = cls.topic.poster

    def test_context(self):
        response = self.client.get(self.url)

        self.assertIsInstance(response.context_data["form"], PostForm)
        self.assertEqual(response.context_data["filters"], Filters.choices)
        self.assertEqual(response.context_data["loadmoretopic_url"], reverse("forum_conversation_extension:topics"))
        self.assertEqual(response.context_data["forum"], self.forum)
        self.assertEqual(response.context_data["active_filter_name"], Filters.ALL.label)

        for filter, label in Filters.choices:
            with self.subTest(filter=filter, label=label):
                response = self.client.get(self.url + f"?filter={filter}")
                self.assertEqual(
                    response.context_data["loadmoretopic_url"],
                    reverse("forum_conversation_extension:topics") + f"?filter={filter}",
                )
                self.assertEqual(response.context_data["active_filter_name"], label)

        response = self.client.get(self.url + "?filter=FAKE")
        self.assertEqual(response.context_data["active_filter_name"], Filters.ALL.label)

    def test_has_liked(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

    def test_queryset(self):
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM, with_public_perms=True))
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.NEWS, with_public_perms=True))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["total"], 1)

        for topic in Topic.objects.exclude(id=self.topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

        for topic in Topic.objects.filter(id=self.topic.id):
            with self.subTest(topic):
                self.assertContains(response, topic.subject)

    def test_queryset_for_unanswered_topic(self):
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM, with_public_perms=True))
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.NEWS, with_public_perms=True))

        response = self.client.get(self.url + "?filter=NEW")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["total"], 1)
        self.assertContains(response, self.topic.subject)

        for topic in Topic.objects.exclude(id=self.topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

    def test_queryset_for_certified_topic(self):
        certified_topic = TopicFactory(
            with_post=True, with_certified_post=True, forum=ForumFactory(with_public_perms=True)
        )
        TopicFactory(
            with_post=True,
            with_certified_post=True,
            forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM, with_public_perms=True),
        )

        response = self.client.get(self.url + "?filter=CERTIFIED")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["total"], 1)
        self.assertContains(response, certified_topic.subject)
        self.assertContains(response, certified_topic.certified_post.post.content.raw[:100])

        for topic in Topic.objects.exclude(id=certified_topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

    def test_pagination(self):
        self.client.force_login(self.user)
        TopicFactory.create_batch(9, with_post=True, forum=self.forum)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.url + "?page=2")

        TopicFactory(with_post=True, forum=self.forum)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.url + "?page=2")

    def test_add_multiple_params_in_query(self):
        TopicFactory.create_batch(12, with_post=True, forum=self.forum, poster=self.user)
        self.client.force_login(self.user)

        for filter in [Filters.ALL, Filters.NEW]:
            with self.subTest(filter=filter):
                response = self.client.get(self.url + f"?filter={filter}")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.url + f"?filter={filter}&amp;page=2")

    def test_filter_dropdown_visibility(self):
        response = self.client.get(self.url)
        self.assertContains(response, '<div class="dropdown-menu dropdown-menu-right" id="filterTopicsDropdown">')
        self.assertEqual(response.context_data["display_filter_dropdown"], True)

        response = self.client.get(self.url + "?page=1")
        self.assertNotContains(response, '<div class="dropdown-menu dropdown-menu-right" id="filterTopicsDropdown">')
        self.assertEqual(response.context_data["display_filter_dropdown"], False)

    def test_template_name(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "forum_conversation/topics_public.html")

        response = self.client.get(self.url, **{"HTTP_HX_REQUEST": "true"})
        self.assertTemplateUsed(response, "forum_conversation/topic_list.html")


class NewsFeedTopicListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("forum_conversation_extension:newsfeed")

    def test_template_name(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "forum_conversation/topics_newsfeed.html")

        response = self.client.get(self.url, **{"HTTP_HX_REQUEST": "true"})
        self.assertTemplateUsed(response, "forum_conversation/topic_list_newsfeed.html")

    def test_queryset(self):
        news_topics = TopicFactory.create_batch(
            2, with_post=True, forum=ForumFactory(kind=ForumKind.NEWS, with_public_perms=True)
        )
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM, with_public_perms=True))
        TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PUBLIC_FORUM, with_public_perms=True))

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context_data["topics"], [topic for topic in news_topics[::-1]])

    def test_context_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["forum"], None)
        self.assertEqual(response.context_data["loadmoretopic_url"], reverse("forum_conversation_extension:newsfeed"))
