from unittest.mock import patch

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
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.notification.factories import BouncedEmailFactory
from lacommunaute.users.factories import UserFactory


TopicReadTrack = get_model("forum_tracking", "TopicReadTrack")
ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
faker = Faker()


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

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.topic.subject)
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

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse(
                "forum_conversation_extension:topic_list",
                kwargs={"forum_pk": self.topic.forum.pk, "forum_slug": self.topic.forum.slug},
            ),
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


class TopicLikeViewTest(TestCase):
    """testing view dedicated in handling HTMX requests"""

    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory()
        cls.user = cls.topic.poster
        cls.url = reverse(
            "forum_conversation_extension:like_topic",
            kwargs={
                "forum_pk": cls.topic.forum.pk,
                "forum_slug": cls.topic.forum.slug,
                "pk": cls.topic.pk,
                "slug": cls.topic.slug,
            },
        )

    def test_get(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_anonymous(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        # vincentporte : response contains redirection, how to handle it through HTMX Post Request ?
        self.assertEqual(response.url, reverse("inclusion_connect:authorize") + "?next=" + self.url)

    def test_post_without_permission(self):
        self.client.force_login(UserFactory())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_post_like_unlike_topic(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill" aria-hidden="true"></i><span class="ml-1">1</span>')

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line" aria-hidden="true"></i><span class="ml-1">0</span>')

    def test_post_topic_not_found(self):
        assign_perm("can_read_forum", self.user, self.topic.forum)
        self.client.force_login(self.user)

        bad_slug_url = reverse(
            "forum_conversation_extension:like_topic",
            kwargs={
                "forum_pk": self.topic.forum.pk,
                "forum_slug": self.topic.forum.slug,
                "pk": 9999999,
                "slug": self.topic.slug,
            },
        )

        self.assertEqual(0, Topic.objects.get(id=self.topic.pk).likers.count())

        response = self.client.post(bad_slug_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(0, Topic.objects.get(id=self.topic.pk).likers.count())

    def test_topic_is_marked_as_read_when_liking(self):
        # need an other unread topic to get TopicReadTrack
        # otherwise (when all topics are read), machina deletes
        # all TopicReadTrack and create/update ForumReadTrack
        TopicFactory(forum=self.topic.forum, poster=self.user)
        self.assertFalse(TopicReadTrack.objects.count())

        assign_perm("can_see_forum", self.user, self.topic.forum)
        assign_perm("can_read_forum", self.user, self.topic.forum)

        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, TopicReadTrack.objects.count())


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

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.content)
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

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, topic.certified_post.post.content)
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

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.topic.first_post.content)  # original post content excluded
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

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, post.poster_display_name)

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
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.topic.first_post.content)  # original post content excluded
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
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-line" aria-hidden="true"></i><span class="ml-1">0</span>')

        UpVoteFactory(post=post, voter=UserFactory())
        UpVoteFactory(post=post, voter=self.user)

        response = view.get(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<i class="ri-star-fill" aria-hidden="true"></i><span class="ml-1">2</span>')

    def test_certified_post_highlight(self):
        post = PostFactory(topic=self.topic, poster=self.user)
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Certifié par la Plateforme de l'Inclusion")

        CertifiedPostFactory(topic=self.topic, post=post, user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion")


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
        cls.content = faker.text(max_nb_chars=20)

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

        self.assertEqual(response.status_code, 500)

    @patch(
        "lacommunaute.forum_conversation.views_htmx.PostFeedCreateView.perform_permissions_check", return_value=True
    )
    @patch("machina.apps.forum_permission.handler.PermissionHandler.can_post_without_approval", return_value=True)
    def test_create_post_as_authenticated_user(self, *args):
        self.client.force_login(self.user)

        response = self.client.post(self.url, data={"content": self.content})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.content)
        self.assertIsInstance(response.context["form"], PostForm)
        self.assertEqual(1, ForumReadTrack.objects.count())
        self.assertContains(response, '<i class="ri-star-line" aria-hidden="true"></i><span class="ml-1">0</span>')
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 2)
        self.assertEqual(
            self.topic.posts.values("content", "username", "approved").last(),
            {"content": self.content, "username": None, "approved": True},
        )

    @patch(
        "lacommunaute.forum_conversation.views_htmx.PostFeedCreateView.perform_permissions_check", return_value=True
    )
    @patch("machina.apps.forum_permission.handler.PermissionHandler.can_post_without_approval", return_value=True)
    def test_create_post_as_bounced_not_bounced_anonymous(self, *args):
        username = faker.email()

        response = self.client.post(self.url, {"content": self.content, "username": username})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.content)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 2)
        self.assertEqual(
            self.topic.posts.values("content", "username", "approved").last(),
            {"content": self.content, "username": username, "approved": True},
        )

        BouncedEmailFactory(email=username).save()

        response = self.client.post(self.url, {"content": self.content, "username": username})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.content)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.posts.count(), 3)
        self.assertEqual(
            self.topic.posts.values("content", "username", "approved").last(),
            {"content": self.content, "username": username, "approved": False},
        )


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

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<div id="showmorepostsarea{self.topic.pk}">')
        self.assertTemplateUsed(response, "forum_conversation/partials/posts_list.html")
