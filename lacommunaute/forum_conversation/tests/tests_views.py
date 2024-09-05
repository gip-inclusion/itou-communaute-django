import pytest  # noqa
from django.conf import settings
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class

from pytest_django.asserts import assertContains, assertNotContains
from taggit.models import Tag

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum_conversation.enums import Filters
from lacommunaute.forum_conversation.factories import (
    AnonymousPostFactory,
    AnonymousTopicFactory,
    CertifiedPostFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.views import PostDeleteView, TopicCreateView
from lacommunaute.forum_moderation.factories import BlockedDomainNameFactory, BlockedEmailFactory
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


faker = Faker(settings.LANGUAGE_CODE)

PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class TopicCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poster = UserFactory()
        cls.forum = ForumFactory(with_public_perms=True)
        cls.url = (
            reverse(
                "forum_conversation:topic_create",
                kwargs={
                    "forum_slug": cls.forum.slug,
                    "forum_pk": cls.forum.pk,
                },
            )
            + "?checked=1"
        )

        cls.post_data = {"subject": faker.text(max_nb_chars=10), "content": faker.paragraph(nb_sentences=5)}

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

    def test_topic_create_as_anonymous_user(self, *args):
        self.post_data["username"] = faker.email()

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        topic = Topic.objects.get()
        self.assertEqual(self.post_data["subject"], topic.subject)
        self.assertEqual(self.post_data["subject"], topic.first_post.subject)
        self.assertEqual(self.post_data["content"], topic.first_post.content.raw)
        self.assertEqual(self.post_data["username"], topic.first_post.username)
        self.assertTrue(topic.approved)
        self.assertTrue(topic.first_post.approved)

    def test_topic_create_as_unapproved_anonymous_user(self, *args):
        self.post_data["username"] = faker.email()
        BlockedEmailFactory(email=self.post_data["username"])

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertEqual(Topic.objects.count(), 0)

    def test_topic_create_with_nonfr_content(self, *args):
        self.client.force_login(self.poster)
        self.post_data["content"] = "популярные лучшие песни слушать онлайн"

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertEqual(Topic.objects.count(), 0)

    def test_topic_create_with_html_content(self, *args):
        self.client.force_login(self.poster)
        self.post_data["content"] = "<p>la communaute</p>"

        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertEqual(Topic.objects.count(), 0)

    def test_topic_create_as_anonymous_user_with_blocked_domain_name(self, *args):
        self.post_data["username"] = "spam@blocked.com"
        BlockedDomainNameFactory(domain="blocked.com")
        response = self.client.post(
            self.url,
            self.post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertEqual(Topic.objects.count(), 0)

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

        self.assertContains(response, Tag.objects.first().name, status_code=200)
        self.assertContains(response, Tag.objects.last().name)

    def test_checked_tags_are_saved(self, *args):
        Tag.objects.bulk_create([Tag(name=f"tag_y{i}", slug=f"tag_y{i}") for i in range(3)])
        self.client.force_login(self.poster)
        post_data = {
            "subject": faker.text(max_nb_chars=5),
            "content": faker.paragraph(nb_sentences=5),
            "tags": [Tag.objects.first().pk, Tag.objects.last().pk],
        }

        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        topic = Topic.objects.get()
        self.assertEqual(2, topic.tags.count())
        self.assertEqual(list(topic.tags.all()), [Tag.objects.first(), Tag.objects.last()])


class TestTopicCreateView:
    def test_redirections_on_forum(self, db, client, snapshot):
        forum = ForumFactory(with_public_perms=True)
        url = reverse("forum_conversation:topic_create", kwargs={"forum_pk": forum.pk, "forum_slug": forum.slug})

        response = client.get(url)
        assert response.status_code == 302
        assert response.url == reverse(
            "forum_conversation_extension:topic_create_check", kwargs={"forum_pk": forum.pk, "forum_slug": forum.slug}
        )

        response = client.get(url + "?checked=1")
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="#div_id_content")
        assert str(content) == snapshot(name="topic_create")

    def test_redirections_on_documentation_forum(self, db, client, snapshot):
        forum = CategoryForumFactory(with_child=True, with_public_perms=True).get_children().first()
        response = client.get(
            reverse("forum_conversation:topic_create", kwargs={"forum_pk": forum.pk, "forum_slug": forum.slug})
        )
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="#div_id_content")
        assert str(content) == snapshot(name="topic_create")

    def test_create_with_new_tags(self, db, client):
        forum = ForumFactory(with_public_perms=True)
        client.force_login(UserFactory())
        tags_list = [faker.word() for i in range(2)]
        response = client.post(
            reverse("forum_conversation:topic_create", kwargs={"forum_pk": forum.pk, "forum_slug": forum.slug}),
            {
                "subject": faker.sentence(),
                "content": faker.paragraph(nb_sentences=5),
                "new_tags": ", ".join(tags_list),
            },
            follow=True,
        )
        assert response.status_code == 200

        queryset = forum.topics.get().tags.filter(name__in=tags_list)
        assert all(tag in queryset.values_list("name", flat=True) for tag in tags_list)

    def test_create_without_tag(self, db, client):
        forum = ForumFactory(with_public_perms=True)
        client.force_login(UserFactory())
        response = client.post(
            reverse("forum_conversation:topic_create", kwargs={"forum_pk": forum.pk, "forum_slug": forum.slug}),
            {
                "subject": faker.sentence(),
                "content": faker.paragraph(nb_sentences=5),
            },
            follow=True,
        )
        assert response.status_code == 200
        assert forum.topics.get().tags.count() == 0


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
        cls.initial_raw_content = cls.topic.first_post.content.raw

    def test_delete_post_button_is_shown(self):
        self.client.force_login(self.poster)
        response = self.client.get(self.url)
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
            status_code=200,
        )

    def test_topic_is_marked_as_read_when_updated(self):
        # evaluating ForumReadTrack instead of TopicReadTrack
        # because of django-machina logic
        self.assertFalse(ForumReadTrack.objects.count())

        self.client.force_login(self.poster)

        post_data = {"subject": "s", "content": faker.paragraph(nb_sentences=5)}
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

        checked_box = f'class="form-check-input" type="checkbox" name="tags" value="{linked_tag.id}" checked="">'
        self.assertContains(response, checked_box, status_code=200)
        not_checked_box = f'class="form-check-input" type="checkbox" name="tags" value="{tag.id}" >'
        self.assertContains(response, not_checked_box)

    def test_update_by_anonymous_user(self):
        topic = AnonymousTopicFactory(with_post=True, forum=self.forum)
        session = self.client.session
        session["_anonymous_forum_key"] = topic.first_post.anonymous_key
        session.save()
        updated_subject = faker.pystr().lower()

        response = self.client.post(
            reverse(
                "forum_conversation:topic_update",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "slug": topic.slug,
                    "pk": topic.pk,
                },
            ),
            {"subject": updated_subject, "content": faker.paragraph(nb_sentences=5), "username": "foo@email.com"},
        )
        self.assertRedirects(
            response,
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "slug": topic.slug,
                    "pk": topic.pk,
                },
            ),
        )

    def test_topic_update_with_nonfr_content(self, *args):
        self.client.force_login(self.poster)
        post_data = {"subject": "s", "content": "популярные лучшие песни слушать онлайн"}

        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.initial_raw_content, self.topic.first_post.content.raw)

    def test_topic_update_with_html_content(self, *args):
        self.client.force_login(self.poster)
        post_data = {"subject": "s", "content": "<p>la communaute</p>"}

        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.initial_raw_content, self.topic.first_post.content.raw)

    def test_topic_update_with_blocked_domain_name(self, *args):
        topic = AnonymousTopicFactory(with_post=True, forum=self.forum)
        initial_raw_content = topic.first_post.content.raw
        session = self.client.session
        session["_anonymous_forum_key"] = topic.first_post.anonymous_key
        session.save()
        BlockedDomainNameFactory(domain="blackhat.com")

        response = self.client.post(
            reverse(
                "forum_conversation:topic_update",
                kwargs={
                    "forum_slug": self.forum.slug,
                    "forum_pk": self.forum.pk,
                    "slug": topic.slug,
                    "pk": topic.pk,
                },
            ),
            {"subject": "subject", "content": "La communauté", "username": "foo@blackhat.com"},
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        topic.refresh_from_db()
        self.assertEqual(topic.first_post.content.raw, initial_raw_content)


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
        cls.post_data = {"content": faker.paragraph(nb_sentences=5)}
        cls.initial_raw_content = cls.post.content.raw

    def test_delete_post_button_is_visible(self, *args):
        self.client.force_login(self.poster)

        response = self.client.get(self.url)

        self.assertContains(response, reverse("forum_conversation:post_delete", kwargs=self.kwargs), status_code=200)

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

    def test_update_post_as_anonymous_user(self, *args):
        post = AnonymousPostFactory(topic=self.topic)
        session = self.client.session
        session["_anonymous_forum_key"] = post.anonymous_key
        session.save()
        url = reverse(
            "forum_conversation:post_update",
            kwargs={
                "forum_slug": self.forum.slug,
                "forum_pk": self.forum.pk,
                "topic_slug": self.topic.slug,
                "topic_pk": self.topic.pk,
                "pk": post.pk,
            },
        )

        post_data = {"content": faker.paragraph(nb_sentences=5), "username": post.username}

        response = self.client.post(
            url,
            post_data,
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertTrue(post.approved)

        BlockedEmailFactory(email=post.username)

        response = self.client.post(
            url,
            {"content": faker.paragraph(nb_sentences=5), "username": post.username},
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        post.refresh_from_db()
        self.assertEqual(post.content.raw, post_data["content"])

    def test_update_post_with_nonfr_content(self, *args):
        self.client.force_login(self.poster)
        post_data = {"content": "популярные лучшие песни слушать онлайн"}

        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.post.refresh_from_db()
        self.assertEqual(self.initial_raw_content, self.post.content.raw)

    def test_update_post_with_html_content(self, *args):
        self.client.force_login(self.poster)
        post_data = {"content": "<p>la communaute</p>"}

        response = self.client.post(
            self.url,
            post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.content.raw, self.initial_raw_content)

    def test_update_post_with_blocked_domain_name(self, *args):
        # add post.anonymous_key to session var to bypass the permissions check
        post = AnonymousPostFactory(topic=self.topic, username="john@doe.com")
        session = self.client.session
        session["_anonymous_forum_key"] = post.anonymous_key
        session.save()
        url = reverse(
            "forum_conversation:post_update",
            kwargs={
                "forum_slug": self.forum.slug,
                "forum_pk": self.forum.pk,
                "topic_slug": self.topic.slug,
                "topic_pk": self.topic.pk,
                "pk": post.pk,
            },
        )

        post_data = {"content": post.content.raw, "username": "spam@blocked.com"}
        BlockedDomainNameFactory(domain="blocked.com")

        response = self.client.post(
            url,
            post_data,
            follow=True,
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertContains(
            response,
            '<form method="post" action="." class="form" enctype="multipart/form-data" novalidate>',
            status_code=200,
        )
        self.assertContains(
            response,
            (
                '<input type="email" name="username" value="spam@blocked.com" maxlength="254" '
                'class="form-control" required id="id_username">'
            ),
            status_code=200,
        )
        post.refresh_from_db()
        self.assertEqual(post.username, "john@doe.com")


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

    def test_post_has_no_upvote(self):
        PostFactory(topic=self.topic, poster=self.poster)
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertContains(
            response, '<i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>0</span>', status_code=200
        )

    def test_post_has_upvote_by_user(self):
        PostFactory(topic=self.topic, poster=self.poster)
        UpVoteFactory(content_object=self.topic.last_post, voter=self.poster)
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertContains(
            response, '<i class="ri-bookmark-fill me-1" aria-hidden="true"></i><span>1</span>', status_code=200
        )

    def test_certified_post_is_highlighted(self):
        post = PostFactory(topic=self.topic, poster=self.poster)
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Certifié par la Plateforme de l'Inclusion")

        CertifiedPostFactory(topic=self.topic, post=post, user=self.poster)
        response = self.client.get(self.url)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion", status_code=200)

    def test_has_tags(self):
        tag = f"tag_{faker.word()}"
        self.client.force_login(self.poster)

        response = self.client.get(self.url)
        self.assertNotContains(response, tag, status_code=200)

        self.topic.tags.add(tag)

        response = self.client.get(self.url)
        self.assertContains(response, tag, status_code=200)

    def test_edit_link_is_visible(self):
        self.client.force_login(self.poster)
        assign_perm("can_edit_own_posts", self.poster, self.forum)

        response = self.client.get(self.url)
        self.assertContains(response, reverse("forum_conversation:topic_update", kwargs=self.kwargs), status_code=200)

    def test_delete_link_visibility(self):
        self.client.force_login(self.poster)
        assign_perm("can_delete_posts", self.poster, self.forum)

        response = self.client.get(self.url)
        self.assertContains(
            response,
            reverse("forum_moderation_extension:topic_delete", kwargs={"slug": self.topic.slug, "pk": self.topic.pk}),
            status_code=200,
        )

    def test_get_marks_notifications_read(self):
        self.client.force_login(self.poster)

        notification = NotificationFactory(recipient=self.poster.email, post=self.topic.first_post)
        self.assertIsNone(notification.sent_at)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        notification.refresh_from_db()
        self.assertEqual(str(notification.created), str(notification.sent_at))

    def test_numqueries(self):
        PostFactory.create_batch(10, topic=self.topic, poster=self.poster)
        UpVoteFactory(content_object=self.topic.last_post, voter=UserFactory())
        CertifiedPostFactory(topic=self.topic, post=self.topic.last_post, user=UserFactory())
        self.client.force_login(self.poster)

        # note vincentporte : to be optimized
        with self.assertNumQueries(39):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


@pytest.mark.parametrize("tag", ["lower", "UPPER"])
def test_queryset_filtered_on_tag(client, db, tag):
    forum = ForumFactory(with_public_perms=True)
    other_topic = TopicFactory(with_post=True, forum=forum)
    tagged_topic = TopicFactory(with_post=True, forum=forum, with_tags=[tag])

    response = client.get(reverse("forum_conversation_extension:topics"), data={"tags": tag})
    assert response.context_data["paginator"].count == 1
    assertContains(response, tagged_topic.subject)
    assertNotContains(response, other_topic.subject)


def test_queryset_for_tagged_topic(client, db, snapshot):
    tags = ["buckley", "jeff"]
    tagged_topic = TopicFactory(with_post=True, with_tags=tags)
    untagged_topic = TopicFactory(with_post=True)

    response = client.get(reverse("forum_conversation_extension:topics"), {"tags": tags[0]})
    content = parse_response_to_soup(response, selector="#topic-list-filter-header")
    assert str(content) == snapshot(name="tagged_topic")
    assertContains(response, tagged_topic.subject)
    assertNotContains(response, untagged_topic.subject)

    TopicFactory(with_post=True, with_tags=tags)
    response = client.get(reverse("forum_conversation_extension:topics"), {"tags": tags[0]})
    content = parse_response_to_soup(response, selector="#topic-list-filter-header")
    assert str(content) == snapshot(name="tagged_topics")


def test_breadcrumbs_on_topic_view(client, db, snapshot):
    discussion_area_forum = ForumFactory(with_public_perms=True)
    category_forum = CategoryForumFactory(with_public_perms=True, with_child=True, name="D Category")

    documentation_topic = TopicFactory(with_post=True, forum=category_forum.get_children().first())
    discussion_area_toplevel_topic = TopicFactory(with_post=True, forum=discussion_area_forum)
    discussion_area_topic = TopicFactory(
        with_post=True, forum=ForumFactory(with_public_perms=True, parent=discussion_area_forum, name="Forum B")
    )

    response = client.get(
        reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": documentation_topic.forum.pk,
                "forum_slug": documentation_topic.forum.slug,
                "pk": documentation_topic.pk,
                "slug": documentation_topic.slug,
            },
        )
    )
    assert response.status_code == 200
    content = parse_response_to_soup(
        response, selector="nav.c-breadcrumb", replace_in_href=[category_forum, documentation_topic.forum]
    )
    assert str(content) == snapshot(name="documentation_topic")

    response = client.get(
        reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": discussion_area_toplevel_topic.forum.pk,
                "forum_slug": discussion_area_toplevel_topic.forum.slug,
                "pk": discussion_area_toplevel_topic.pk,
                "slug": discussion_area_toplevel_topic.slug,
            },
        )
    )
    assert response.status_code == 200
    content = parse_response_to_soup(response, selector="nav.c-breadcrumb")
    assert str(content) == snapshot(name="discussion_area_toplevel_topic")

    response = client.get(
        reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": discussion_area_topic.forum.pk,
                "forum_slug": discussion_area_topic.forum.slug,
                "pk": discussion_area_topic.pk,
                "slug": discussion_area_topic.slug,
            },
        )
    )
    assert response.status_code == 200
    content = parse_response_to_soup(
        response, selector="nav.c-breadcrumb", replace_in_href=[discussion_area_topic.forum]
    )
    assert str(content) == snapshot(name="discussion_area_topic")


class TopicListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("forum_conversation_extension:topics")
        cls.forum = ForumFactory(with_public_perms=True)
        cls.topic = TopicFactory(with_post=True, forum=cls.forum)
        cls.user = cls.topic.poster

    def test_context(self):
        response = self.client.get(self.url)

        self.assertIsInstance(response.context_data["form"], PostForm)
        self.assertEqual(response.context_data["filters"], Filters.choices)
        self.assertEqual(response.context_data["loadmoretopic_url"], reverse("forum_conversation_extension:topics"))
        self.assertEqual(response.context_data["forum"], self.forum)
        self.assertEqual(response.context_data["active_filter_name"], Filters.ALL.label)
        self.assertEqual(response.context_data["active_tags"], "")

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

    def test_context_with_tag(self):
        tags = [Tag.objects.create(name=faker.sentence()) for i in range(2)]
        response = self.client.get(self.url, {"tags": ",".join([tag.slug for tag in tags])})
        self.assertEqual(response.context_data["active_tags"], ",".join([tag.slug for tag in tags]))
        self.assertEqual(response.context_data["active_tags_label"], " ou ".join([tag.name for tag in tags]))

    def test_queryset(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["paginator"].count, 1)

        for topic in Topic.objects.exclude(id=self.topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

        for topic in Topic.objects.filter(id=self.topic.id):
            with self.subTest(topic):
                self.assertContains(response, topic.subject)

    def test_queryset_for_unanswered_topic(self):
        # answered topic
        PostFactory(topic=TopicFactory(with_post=True, forum=self.forum))
        response = self.client.get(self.url + "?filter=NEW")
        self.assertEqual(response.context_data["paginator"].count, 1)
        self.assertContains(response, self.topic.subject, status_code=200)

        for topic in Topic.objects.exclude(id=self.topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

    def test_queryset_for_certified_topic(self):
        certified_topic = TopicFactory(
            with_post=True, with_certified_post=True, forum=ForumFactory(with_public_perms=True)
        )

        response = self.client.get(self.url + "?filter=CERTIFIED")
        self.assertEqual(response.context_data["paginator"].count, 1)
        self.assertContains(response, certified_topic.subject, status_code=200)
        self.assertContains(response, certified_topic.certified_post.post.content.raw[:100])

        for topic in Topic.objects.exclude(id=certified_topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

    def test_pagination(self):
        self.client.force_login(self.user)
        TopicFactory.create_batch(9, with_post=True, forum=self.forum)

        response = self.client.get(self.url)
        self.assertNotContains(response, self.url + "?page=2", status_code=200)

        TopicFactory(with_post=True, forum=self.forum)

        response = self.client.get(self.url)
        self.assertContains(response, self.url + "?page=2", status_code=200)

    def test_showmoretopics_url_with_params(self):
        tag_list = ["iae", "siae", "prescripteur"]
        TopicFactory.create_batch(12, with_post=True, forum=self.forum, poster=self.user, with_tags=tag_list)
        self.client.force_login(self.user)

        params = [
            {"filter": filter, "tags": tags}
            for filter in ["ALL", "NEW", None]
            for tags in tag_list + [",".join(tag_list), None]
        ]

        for param in params:
            with self.subTest(param=param):
                encoded_params = urlencode({k: v for k, v in param.items() if v})
                url_with_params = self.url + f"?{encoded_params}" if encoded_params else self.url
                expected_url = (
                    url_with_params.replace("&", "&amp;") + "&amp;page=2" if encoded_params else self.url + "?page=2"
                )
                response = self.client.get(url_with_params)
                self.assertContains(response, expected_url, status_code=200)

    def test_filter_dropdown_visibility(self):
        response = self.client.get(self.url)
        self.assertContains(response, '<div class="dropdown-menu dropdown-menu-end" id="filterTopicsDropdown">')
        self.assertEqual(response.context_data["filter_dropdown_endpoint"], self.url)

        response = self.client.get(self.url + "?page=1")
        self.assertNotContains(response, '<div class="dropdown-menu dropdown-menu-end" id="filterTopicsDropdown">')
        self.assertEqual(response.context_data["filter_dropdown_endpoint"], None)

    def test_filter_dropdown_with_tags(self):
        tag = Tag.objects.create(name=faker.words(nb=3))
        response = self.client.get(self.url + f"?tags={tag.slug}")
        self.assertContains(response, f'hx-get="/topics/?filter=ALL&tags={tag.slug}"')
        self.assertContains(response, f'hx-get="/topics/?filter=NEW&tags={tag.slug}"')
        self.assertContains(response, f'hx-get="/topics/?filter=CERTIFIED&tags={tag.slug}"')

    def test_template_name(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "forum_conversation/topics_public.html")

        response = self.client.get(self.url, **{"HTTP_HX_REQUEST": "true"})
        self.assertTemplateUsed(response, "forum_conversation/topic_list.html")


class TestTopicListView:
    def test_clickable_tags(self, client, db, snapshot):
        forum = ForumFactory(with_public_perms=True)
        TopicFactory(with_post=True, forum=forum, with_tags=["tag"])

        response = client.get(reverse("forum_conversation_extension:topics"))
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector="a.tag")) == snapshot(name="clickable_tags_page1")

        # add 10 Topics before the tagged one to put it on the second page
        TopicFactory.create_batch(10, with_post=True, forum=forum)

        response = client.get(reverse("forum_conversation_extension:topics") + "?page=2")
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector="a.tag")) == snapshot(name="clickable_tags_page2")


class TestPosterTemplate:
    def test_topic_in_topics_view(self, client, db, snapshot):
        topic = TopicFactory(with_post=True, poster=UserFactory(first_name="Jeff", last_name="Buckley"))
        response = client.get(reverse("forum_conversation_extension:topics"))
        soup = parse_response_to_soup(
            response, replace_in_href=[(topic.poster.username, "poster_username")], selector=".poster-infos"
        )
        assert str(soup) == snapshot(name="topic_in_topics_view")

    def test_topic_from_other_public_forum_in_topics_view(self, client, db, snapshot):
        # first_public_forum
        ForumFactory(with_public_perms=True)

        topic = TopicFactory(
            with_post=True,
            forum=ForumFactory(with_public_perms=True, name="Abby's Forum"),
            poster=UserFactory(first_name="Alan", last_name="Turing"),
        )
        response = client.get(reverse("forum_conversation_extension:topics"))
        soup = parse_response_to_soup(
            response,
            replace_in_href=[
                (topic.poster.username, "poster_username"),
                (
                    reverse("forum_extension:forum", kwargs={"slug": topic.forum.slug, "pk": topic.forum.pk}),
                    "forum_url",
                ),
            ],
            selector=".poster-infos",
        )
        assert str(soup) == snapshot(name="topic_from_other_public_forum_in_topics_view")

    def test_topic_in_its_own_public_forum(self, client, db, snapshot):
        # first_public_forum
        ForumFactory(with_public_perms=True)

        topic = TopicFactory(
            with_post=True,
            forum=ForumFactory(with_public_perms=True, name="Joe's Forum"),
            poster=UserFactory(first_name="Dermot", last_name="Turing"),
        )
        response = client.get(
            reverse("forum_extension:forum", kwargs={"slug": topic.forum.slug, "pk": topic.forum.pk})
        )
        soup = parse_response_to_soup(
            response, replace_in_href=[(topic.poster.username, "poster_username")], selector=".poster-infos"
        )
        assert str(soup) == snapshot(name="topic_in_its_own_public_forum")


class TestTopicCreateCheckView:
    def test_get_method(self, client, db, snapshot):
        forum = ForumFactory(name="forum")
        response = client.get(
            reverse(
                "forum_conversation_extension:topic_create_check",
                kwargs={"forum_slug": forum.slug, "forum_pk": forum.pk},
            )
        )
        assert response.status_code == 200
        assertContains(
            response,
            reverse("forum_conversation:topic_create", kwargs={"forum_slug": forum.slug, "forum_pk": forum.pk})
            + "?checked",
        )
        content = parse_response_to_soup(response, selector="main", replace_in_href=[forum])
        assert str(content) == snapshot(name="topic_create_check")

    def test_forum_does_not_exist(self, client, db):
        response = client.get(
            reverse("forum_conversation_extension:topic_create_check", kwargs={"forum_slug": "fake", "forum_pk": 999})
        )
        assert response.status_code == 404

    def test_post_method_not_allowed(self, client, db):
        forum = ForumFactory()
        response = client.post(
            reverse(
                "forum_conversation_extension:topic_create_check",
                kwargs={"forum_slug": forum.slug, "forum_pk": forum.pk},
            )
        )
        assert response.status_code == 405
