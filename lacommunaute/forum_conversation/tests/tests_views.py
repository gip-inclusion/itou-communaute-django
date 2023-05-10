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

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.views import PostDeleteView, TopicCreateView, TopicUpdateView
from lacommunaute.forum_upvote.factories import CertifiedPostFactory, UpVoteFactory
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
        cls.forum = ForumFactory()
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:topic_create",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
            },
        )
        assign_perm("can_read_forum", cls.poster, cls.forum)
        assign_perm("can_see_forum", cls.poster, cls.forum)

    def test_redirection(self):
        topic = TopicFactory(forum=self.forum, poster=self.poster, with_post=True)
        view = TopicCreateView()
        view.forum_post = topic.posts.first()
        self.assertEqual(
            view.get_success_url(),
            reverse("forum_extension:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )

    def test_delete_button_is_hidden(self):
        assign_perm("can_start_new_topics", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, '/post/delete/" title="Supprimer" role="button" class="btn btn-outline-danger">Supprimer</a>'
        )

    def test_topic_is_marked_as_read_when_created(self):
        self.assertFalse(TopicReadTrack.objects.count())

        assign_perm("can_start_new_topics", self.poster, self.forum)
        self.client.force_login(self.poster)

        post_data = {"subject": "s", "content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, TopicReadTrack.objects.count())

    def test_topic_poster_is_added_to_likers_list(self):
        assign_perm("can_start_new_topics", self.poster, self.forum)
        self.client.force_login(self.poster)

        post_data = {"subject": "s", "content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Topic.objects.count())
        self.assertEqual(1, Topic.objects.first().likers.count())

    def test_topic_create_as_anonymous_user(self):
        assign_perm("can_start_new_topics", AnonymousUser(), self.forum)
        assign_perm("can_read_forum", AnonymousUser(), self.forum)

        post_data = {
            "subject": faker.text(max_nb_chars=5),
            "content": faker.text(max_nb_chars=5),
            "username": faker.email(),
        }
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Topic.objects.count())
        topic = Topic.objects.first()
        self.assertEqual(post_data["subject"], topic.subject)
        self.assertEqual(post_data["subject"], topic.first_post.subject)
        self.assertEqual(post_data["content"], topic.first_post.content.raw)
        self.assertEqual(post_data["username"], topic.first_post.username)
        self.assertEqual(0, topic.likers.count())

    def test_tags_checkbox_are_displayed(self):
        Tag.objects.create(name=faker.word())
        Tag.objects.create(name=faker.word())
        assign_perm("can_start_new_topics", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, Tag.objects.first().name)
        self.assertContains(response, Tag.objects.last().name)

    def test_checked_tags_are_saved(self):
        Tag.objects.create(name=faker.word())
        Tag.objects.create(name=faker.word())
        Tag.objects.create(name=faker.word())
        assign_perm("can_start_new_topics", self.poster, self.forum)
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
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:topic_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "slug": cls.topic.slug,
                "pk": cls.topic.pk,
            },
        )
        assign_perm("can_read_forum", cls.poster, cls.topic.forum)
        assign_perm("can_see_forum", cls.poster, cls.topic.forum)

    def test_redirection(self):
        view = TopicUpdateView()
        view.forum_post = self.topic.posts.first()
        self.assertEqual(
            view.get_success_url(),
            reverse("forum_extension:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}),
        )

    def test_has_not_permission_to_delete_post(self):
        assign_perm("can_edit_own_posts", self.poster, self.forum)
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
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

    def test_has_permission_to_delete_post(self):
        assign_perm("can_edit_own_posts", self.poster, self.forum)
        assign_perm("can_delete_own_posts", self.poster, self.forum)
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

        assign_perm("can_edit_own_posts", self.poster, self.forum)
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
        assign_perm("can_edit_own_posts", self.poster, self.forum)
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

    def test_http_forbidden(self):

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
        cls.topic = TopicFactory(with_post=True)
        cls.forum = cls.topic.forum
        cls.poster = cls.topic.poster
        cls.perm_handler = PermissionHandler()
        cls.url = reverse(
            "forum_conversation:post_update",
            kwargs={
                "forum_slug": cls.forum.slug,
                "forum_pk": cls.forum.pk,
                "topic_slug": cls.topic.slug,
                "topic_pk": cls.topic.pk,
                "pk": cls.topic.posts.first().pk,
            },
        )
        assign_perm("can_read_forum", cls.poster, cls.forum)
        assign_perm("can_see_forum", cls.poster, cls.forum)
        assign_perm("can_edit_own_posts", cls.poster, cls.forum)

    def test_has_not_permission_to_delete_post(self):
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
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

    def test_has_permission_to_delete_post(self):
        assign_perm("can_delete_own_posts", self.poster, self.forum)
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

    def test_topic_is_marked_as_read_when_post_is_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        self.client.force_login(self.poster)

        post_data = {"content": "c"}
        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, ForumReadTrack.objects.count())


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
