from django.template.defaultfilters import truncatechars_html
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.http import urlencode
from faker import Faker
from machina.core.loading import get_class

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum.views import ForumView
from lacommunaute.forum_conversation.factories import CertifiedPostFactory, PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
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
        cls.forum = ForumFactory(with_public_perms=True)
        cls.topic = TopicFactory(with_post=True, forum=cls.forum)
        cls.user = cls.topic.poster
        cls.forum = cls.topic.forum

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

        self.assertNotContains(response, f'<a href="{topic_url}"', status_code=200)

        PostFactory.create_batch(2, topic=self.topic, poster=self.user)
        response = self.client.get(self.url)

        self.assertContains(response, f'hx-get="{topic_url}"', status_code=200)
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

        self.assertContains(response, f'hx-get="{topic_url}"', status_code=200)
        self.assertContains(response, "+ voir la suite")
        self.assertEqual(response.context_data["loadmoretopic_suffix"], "topicsinforum")

    def test_has_liked(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, with_like=True)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: solid heart
        self.assertContains(response, '<i class="ri-heart-3-fill mr-1" aria-hidden="true"></i><span>1</span>')

    def test_has_not_liked(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        # icon: regular heart (outlined)
        self.assertContains(response, '<i class="ri-heart-3-line mr-1" aria-hidden="true"></i><span>0</span>')

    def test_has_liked_TOPIC_ANNOUNCE(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, with_like=True, type=Topic.TOPIC_ANNOUNCE)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, '<i class="ri-heart-3-fill mr-1" aria-hidden="true"></i><span>1</span>')

    def test_has_not_liked_TOPIC_ANNOUNCE(self):
        TopicFactory(forum=self.forum, poster=self.user, with_post=True, type=Topic.TOPIC_ANNOUNCE)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertContains(response, '<i class="ri-heart-3-line mr-1" aria-hidden="true"></i><span>0</span>')

    def test_anonymous_like(self):
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
        self.assertContains(response, poll_option.poll.question, status_code=200)
        self.assertContains(response, poll_option.text)

    def test_can_submit_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertIsInstance(response.context_data["form"], PostForm)
        self.assertContains(response, f'id="collapsePost{self.topic.pk}', status_code=200)

    def test_cannot_submit_post(self, *args):
        user = UserFactory()
        forum = ForumFactory()
        assign_perm("can_read_forum", user, forum)
        assign_perm("can_see_forum", user, forum)
        remove_perm("can_reply_to_topics", user, self.forum)
        url = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug})
        self.client.force_login(user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'id="collapsePost{self.topic.pk}')

    def test_queries(self):
        TopicFactory.create_batch(20, with_post=True)
        self.client.force_login(self.user)
        with self.assertNumQueries(22):
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

        self.assertContains(response, truncatechars_html(post.content.rendered, 200), status_code=200)
        self.assertContains(response, topic_certified_post_url)
        self.assertContains(response, "Certifié par la Plateforme de l'Inclusion")

    def test_loadmoretopic_url(self):
        loadmoretopic_url = reverse(
            "forum_conversation_extension:topic_list",
            kwargs={"forum_pk": self.forum.pk, "forum_slug": self.forum.slug},
        )

        TopicFactory.create_batch(9, with_post=True, forum=self.forum)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["loadmoretopic_url"], loadmoretopic_url)

        self.assertNotContains(response, loadmoretopic_url + "?page=2")

        TopicFactory(with_post=True, forum=self.forum)
        response = self.client.get(self.url)
        self.assertContains(response, loadmoretopic_url + "?page=2", status_code=200)

        TopicFactory.create_batch(10, with_post=True, forum=self.forum)
        response = self.client.get(self.url + "?page=2")
        self.assertContains(response, loadmoretopic_url + "?page=3", status_code=200)

    def test_topic_has_tags(self):
        tag = f"tag_{faker.word()}"
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertNotContains(response, tag, status_code=200)

        self.topic.tags.add(tag)
        response = self.client.get(self.url)
        self.assertContains(response, tag, status_code=200)

    def test_description_is_markdown_rendered(self):
        self.forum.description = "# title"
        self.forum.save()
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertContains(response, "<h1>title</h1>", status_code=200)

    def test_descendants_are_in_cards_if_forum_is_category_type(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()
        url = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug})

        response = self.client.get(url)

        self.assertContains(response, '<div class="card-body', status_code=200)
        self.assertContains(response, child_forum.name)
        self.assertContains(
            response, reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )

    def test_siblings_in_context(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()
        url = reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data["forums"].get(), child_forum)
        self.assertEqual(response.context_data["parent_forum"], forum)

    def test_next_url_in_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["next_url"], self.url)

    def test_share_buttons(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()
        url = reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})

        response = self.client.get(url)
        self.assertContains(
            response,
            'div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuSocialShare">',
            status_code=200,
        )

    def test_upvote_actions(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()

        # anonymous
        anonymous_html = (
            '<a href="/inclusion_connect/authorize?next_url=%2Fforum%2F'
            f'{child_forum.slug}-{child_forum.pk}%2F%23{child_forum.pk}"'
            ' rel="nofollow"'
            ' class="btn btn-sm btn-ico-only btn-link btn-secondary" data-toggle="tooltip" data-placement="top"'
            ' title="Connectez-vous pour sauvegarder">'
            '\n                <i class="ri-bookmark-line mr-1" aria-hidden="true"></i><span>0</span>'
        )
        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(response, anonymous_html, status_code=200)

        # authenticated
        self.client.force_login(self.user)
        no_upvote_html = (
            '<button type="submit"'
            '\n                        title="Sauvegarder"'
            '\n                        class="btn btn-sm btn-ico btn-secondary matomo-event px-2"'
            '\n                        data-matomo-category="engagement"'
            '\n                        data-matomo-action="upvote"'
            '\n                        data-matomo-option="post"'
            "\n                >"
            '\n                    <i class="ri-bookmark-line mr-1" aria-hidden="true"></i>'
            "<span>0</span>"
        )
        response = self.client.get(reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": forum.slug}))
        self.assertContains(response, no_upvote_html, status_code=200)

        child_forum.upvotes.create(voter=self.user)
        upvoted_html = (
            '<button type="submit"'
            '\n                        title="Sauvegarder"'
            '\n                        class="btn btn-sm btn-ico btn-secondary matomo-event px-2"'
            '\n                        data-matomo-category="engagement"'
            '\n                        data-matomo-action="upvote"'
            '\n                        data-matomo-option="post"'
            "\n                >"
            '\n                    <i class="ri-bookmark-fill mr-1" aria-hidden="true"></i>'
            "<span>1</span>"
        )
        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(response, upvoted_html, status_code=200)

    def test_upvotes_count(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()

        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(
            response, '<i class="ri-bookmark-line mr-1" aria-hidden="true"></i><span>0</span>', status_code=200
        )

        child_forum.upvotes.create(voter=self.user)

        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(
            response, '<i class="ri-bookmark-line mr-1" aria-hidden="true"></i><span>1</span>', status_code=200
        )

        child_forum.upvotes.create(voter=UserFactory())

        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(
            response, '<i class="ri-bookmark-line mr-1" aria-hidden="true"></i><span>2</span>', status_code=200
        )
