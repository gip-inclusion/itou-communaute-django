from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django.urls import reverse
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class
from taggit.models import Tag

from lacommunaute.forum_conversation.factories import CertifiedPostFactory, PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import CertifiedPost, Topic
from lacommunaute.forum_conversation.views_htmx import PostListView
from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.factories import BlockedDomainNameFactory, BlockedEmailFactory
from lacommunaute.forum_moderation.models import BlockedPost
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.users.factories import UserFactory


faker = Faker(settings.LANGUAGE_CODE)

TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")


class ForumTopicListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.url = reverse(
            "forum_conversation_extension:topic_list",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
            },
        )

    def test_get_forum_not_found(self):
        response = self.client.get(
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={
                    "forum_pk": 999,
                    "forum_slug": self.topic.forum.slug,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get(self):
        other_topic = TopicFactory(with_post=True)
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(response, self.topic.subject, status_code=200)
        self.assertNotContains(response, other_topic.subject)
        self.assertEqual(response.context["forum"], self.topic.forum)

    def test_get_without_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_loadmoretopic_url(self):
        TopicFactory.create_batch(20, forum=self.topic.forum, with_post=True)
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(
            response,
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={"forum_pk": self.topic.forum.pk, "forum_slug": self.topic.forum.slug},
            ),
            status_code=200,
        )
        self.assertEqual(response.context_data["loadmoretopic_suffix"], "topicsinforum")

    def test_numqueries_vs_tags(self):
        tags = Tag.objects.bulk_create([Tag(name=f"tag{i}", slug=f"tag{i}") for i in range(5)])
        for topic in TopicFactory.create_batch(20, forum=self.topic.forum, with_post=True):
            topic.tags.add(", ".join(tag.name for tag in tags))
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        with self.assertNumQueries(13):
            self.client.get(self.url)


class TopicContentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory()
        cls.user = cls.topic.poster
        cls.url = reverse(
            "forum_conversation_extension:showmore_topic",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )

    def test_cannot_read_topic(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_topic_doesnt_exist(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "forum_conversation_extension:showmore_posts",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk + 1,
                    "slug": self.topic.slug,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get_topic_content(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        post = PostFactory(topic=self.topic, poster=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(response, post.content, status_code=200)
        self.assertEqual(1, ForumReadTrack.objects.count())


class TopicCertifiedPostViewTest(TestCase):
    def test_get_topic_certified_post(self):
        topic = TopicFactory(with_certified_post=True)
        user = topic.poster
        assign_perm("can_read_forum", user, topic.forum)
        url = reverse(
            "forum_conversation_extension:showmore_certified",
            kwargs={
                "forum_pk": topic.forum.pk,
                "forum_slug": topic.forum.slug,
                "pk": topic.pk,
                "slug": topic.slug,
            },
        )
        self.client.force_login(user)

        response = self.client.get(url)

        self.assertContains(response, topic.certified_post.post.content, status_code=200)
        self.assertEqual(1, ForumReadTrack.objects.count())


class PostListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        assign_perm("can_read_forum", cls.user, cls.topic.forum)
        cls.kwargs = {
            "forum_pk": cls.topic.forum.pk,
            "forum_slug": cls.topic.forum.slug,
            "pk": cls.topic.pk,
            "slug": cls.topic.slug,
        }
        cls.url = reverse(
            "forum_conversation_extension:showmore_posts",
            kwargs=cls.kwargs,
        )

    def test_cannot_read_post(self):
        self.client.force_login(UserFactory())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_topic_doesnt_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "forum_conversation_extension:showmore_posts",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk + 1,
                    "slug": self.topic.slug,
                },
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get_list_of_posts(self):
        posts = PostFactory.create_batch(2, topic=self.topic, poster=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertNotContains(
            response, self.topic.first_post.content, status_code=200
        )  # original post content excluded
        self.assertContains(response, posts[0].content)
        self.assertContains(response, posts[1].content)
        self.assertContains(response, posts[0].poster_display_name)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(1, ForumReadTrack.objects.count())
        self.assertEqual(response.context["next_url"], self.topic.get_absolute_url())

    def test_get_list_of_posts_posted_by_anonymous_user(self):
        username = faker.email()
        post = PostFactory(topic=self.topic, poster=None, username=username)
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(response, post.poster_display_name, status_code=200)

    def test_get_list_of_posts_linked_to_annonce_topic(self):
        post = PostFactory(topic=self.topic, poster=self.user)
        self.topic.type = Topic.TOPIC_ANNOUNCE
        self.topic.save()

        request = RequestFactory().get(self.url)
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()

        view = PostListView()
        view.request = request
        view.kwargs = self.kwargs

        response = view.get(request)
        self.assertNotContains(
            response, self.topic.first_post.content, status_code=200
        )  # original post content excluded
        self.assertContains(response, post.content)

    def test_upvote_annotations(self):
        post = PostFactory(topic=self.topic, poster=self.user)

        request = RequestFactory().get(self.url)
        request.user = self.user
        request.forum_permission_handler = PermissionHandler()

        view = PostListView()
        view.request = request
        view.kwargs = self.kwargs

        response = view.get(request)
        self.assertContains(
            response, '<i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>0</span>', status_code=200
        )

        UpVoteFactory(content_object=post, voter=UserFactory())
        UpVoteFactory(content_object=post, voter=self.user)

        response = view.get(request)
        self.assertContains(
            response, '<i class="ri-bookmark-fill me-1" aria-hidden="true"></i><span>2</span>', status_code=200
        )

    def test_certified_post_highlight(self):
        post = PostFactory(topic=self.topic, poster=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertNotContains(response, "Certifié par la Plateforme de l'Inclusion", status_code=200)

        CertifiedPostFactory(topic=self.topic, post=post, user=self.user)
        response = self.client.get(self.url)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion", status_code=200)


class PostFeedCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.url = reverse(
            "forum_conversation_extension:post_create",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )
        cls.content = faker.paragraph(nb_sentences=5)

    def test_get_method_unallowed(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_cannot_post(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 403)

    def test_topic_doesnt_exist(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "forum_conversation_extension:post_create",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk + 1,
                    "slug": self.topic.slug,
                },
            ),
            data={},
        )

        self.assertEqual(response.status_code, 404)

    def test_form_is_invalid(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(self.url, data={})

        self.assertContains(response, '<div id="div_id_content" class="form-group has-error">', status_code=200)

    def test_create_post_as_authenticated_user(self, *args):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        assign_perm("can_post_without_approval", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(self.url, data={"content": self.content})

        self.assertContains(response, self.content, status_code=200)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(1, ForumReadTrack.objects.count())
        self.assertContains(response, '<i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>0</span>')
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 2)
        self.assertEqual(
            self.topic.posts.values("content", "username", "approved", "update_reason").last(),
            {"content": self.content, "username": None, "approved": True, "update_reason": None},
        )

    def test_create_post_as_blocked_not_blocked_anonymous(self, *args):
        user = AnonymousUser()
        assign_perm("can_reply_to_topics", user, self.topic.forum)
        assign_perm("can_post_without_approval", user, self.topic.forum)
        username = faker.email()

        response = self.client.post(self.url, {"content": self.content, "username": username})

        self.assertContains(response, self.content, status_code=200)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 2)
        self.assertEqual(
            self.topic.posts.values("content", "username", "approved", "update_reason").last(),
            {"content": self.content, "username": username, "approved": True, "update_reason": None},
        )

        BlockedEmailFactory(email=username).save()

        response = self.client.post(self.url, {"content": self.content, "username": username})

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertContains(
            response,
            (
                f'<input type="email" name="username" value="{username}" maxlength="254" '
                'class="form-control" required id="id_username">'
            ),
            status_code=200,
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 2)

        # the blocked post should be recorded in the database
        blocked_post = BlockedPost.objects.get()
        assert blocked_post.content == self.content
        assert blocked_post.username == username
        assert blocked_post.block_reason == BlockedPostReason.BLOCKED_USER.value

    def test_create_post_with_nonfr_content(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        assign_perm("can_post_without_approval", self.user, self.topic.forum)
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"content": "популярные лучшие песни слушать онлайн"})

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertContains(
            response,
            (
                '<textarea name="content" cols="40" rows="10" placeholder="Entrez votre message" '
                'class="form-control" required id="id_content">'
            ),
            status_code=200,
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 1)

        # the blocked post should be recorded in the database
        blocked_post = BlockedPost.objects.get()
        assert blocked_post.poster == self.user
        assert blocked_post.content == "популярные лучшие песни слушать онлайн"
        assert blocked_post.block_reason == BlockedPostReason.ALTERNATIVE_LANGUAGE.value

    def test_create_post_with_html_content(self):
        assign_perm("can_reply_to_topics", self.user, self.topic.forum)
        assign_perm("can_post_without_approval", self.user, self.topic.forum)
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
            {"content": "<p>Hello, <a href='https://www.example.com'>click here</a> to visit example.com</p>"},
        )

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
            status_code=200,
        )
        self.assertContains(
            response,
            (
                '<textarea name="content" cols="40" rows="10" placeholder="Entrez votre message" '
                'class="form-control" required id="id_content">'
            ),
            status_code=200,
        )
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 1)

        # we don't create a BlockedPost record for HTML content to avoid storing malicious code
        assert BlockedPost.objects.count() == 0

    def test_create_post_with_blocked_domain_name(self):
        BlockedDomainNameFactory(domain="blocked.com")

        user = AnonymousUser()
        assign_perm("can_reply_to_topics", user, self.topic.forum)

        response = self.client.post(self.url, {"content": "la communauté", "username": "spam@blocked.com"})

        self.assertContains(
            response,
            "Votre message ne respecte pas les règles de la communauté.",
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
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 1)

        # the blocked post should be recorded in the database
        blocked_post = BlockedPost.objects.get()
        assert blocked_post.content == "la communauté"
        assert blocked_post.username == "spam@blocked.com"
        assert blocked_post.block_reason == BlockedPostReason.BLOCKED_DOMAIN.value


class CertifiedPostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        assign_perm("can_read_forum", cls.user, cls.topic.forum)
        cls.url = reverse(
            "forum_conversation_extension:certify",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )
        cls.form_data = {"post_pk": cls.topic.last_post.pk}

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_post_instance_doesnt_exist(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data={"post_pk": 9999})
        self.assertEqual(response.status_code, 404)

    def test_certify_without_permission(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 403)

    def test_certify_with_permission(self):
        self.topic.forum.members_group.user_set.add(self.user)
        self.topic.forum.members_group.save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CertifiedPost.objects.count(), 1)
        certified_post = CertifiedPost.objects.first()
        self.assertEqual(certified_post.post, self.topic.last_post)
        self.assertEqual(certified_post.user, self.user)
        self.assertEqual(certified_post.topic, self.topic)
        self.assertEqual(ForumReadTrack.objects.count(), 1)

    def test_uncertify_with_permission(self):
        self.topic.forum.members_group.user_set.add(self.user)
        self.topic.forum.members_group.save()
        CertifiedPost(topic=self.topic, post=self.topic.last_post, user=self.user).save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CertifiedPost.objects.count(), 0)
        self.assertEqual(ForumReadTrack.objects.count(), 1)

    def test_rendered_content(self):
        self.topic.forum.members_group.user_set.add(self.user)
        self.topic.forum.members_group.save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.form_data)

        self.assertContains(response, f'<div id="showmorepostsarea{self.topic.pk}">', status_code=200)
        self.assertTemplateUsed(response, "forum_conversation/partials/posts_list.html")
