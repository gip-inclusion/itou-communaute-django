import pytest  # noqa
import re
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import truncatechars_html
from django.test import RequestFactory, TestCase
from django.urls import reverse
from faker import Faker
from machina.core.loading import get_class
from taggit.models import Tag

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory, ForumRatingFactory
from lacommunaute.forum.models import Forum
from lacommunaute.forum.views import ForumView
from lacommunaute.forum_conversation.enums import Filters
from lacommunaute.forum_conversation.factories import CertifiedPostFactory, PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup, reset_model_sequence_fixture


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


class ForumViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.forum = ForumFactory(with_public_perms=True)
        cls.topic = TopicFactory(with_post=True, forum=cls.forum)
        cls.user = cls.topic.poster
        cls.forum = cls.topic.forum

        cls.url = reverse("forum_extension:forum", kwargs={"pk": cls.forum.pk, "slug": cls.forum.slug})

    def test_context(self):
        response = self.client.get(self.url)

        loadmoretopic_url = reverse("forum_extension:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug})

        self.assertIsInstance(response.context_data["form"], PostForm)
        self.assertEqual(response.context_data["filters"], Filters.choices)
        self.assertEqual(response.context_data["loadmoretopic_url"], loadmoretopic_url)
        self.assertEqual(response.context_data["forum"], self.forum)
        self.assertIsNone(response.context_data["rating"])
        self.assertEqual(response.context_data["active_filter_name"], Filters.ALL.label)
        self.assertEqual(response.context_data["active_tags"], "")

        for filter, label in Filters.choices:
            with self.subTest(filter=filter, label=label):
                response = self.client.get(self.url + f"?filter={filter}")
                self.assertEqual(
                    response.context_data["loadmoretopic_url"],
                    loadmoretopic_url + f"?filter={filter}",
                )
                self.assertEqual(response.context_data["active_filter_name"], label)

        response = self.client.get(self.url + "?filter=FAKE")
        self.assertEqual(response.context_data["active_filter_name"], Filters.ALL.label)

        tag = Tag.objects.create(name="tag_1", slug="tag_1")
        response = self.client.get(self.url + f"?tags=nonexistant,{tag.name}")
        self.assertIn(tag.slug, response.context_data["active_tags"])
        self.assertNotIn("nonexistant", response.context_data["active_tags"])
        self.assertIn(tag.name, response.context_data["active_tags_label"])
        self.assertNotIn("nonexistant", response.context_data["active_tags_label"])

    def test_template_name(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "forum/forum_detail.html")

        response = self.client.get(self.url, **{"HTTP_HX_REQUEST": "true"})
        self.assertTemplateUsed(response, "forum_conversation/topic_list.html")

        documentation_category_forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        documentation_forum = documentation_category_forum.children.first()

        response = self.client.get(documentation_category_forum.get_absolute_url())
        self.assertTemplateUsed(response, "forum/forum_documentation_category.html")

        response = self.client.get(documentation_forum.get_absolute_url())
        self.assertTemplateUsed(response, "forum/forum_documentation.html")

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
        ContentType.objects.clear_cache()

        TopicFactory.create_batch(20, with_post=True)
        self.client.force_login(self.user)
        with self.assertNumQueries(23):
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
            "forum_extension:forum",
            kwargs={"pk": self.forum.pk, "slug": self.forum.slug},
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

    def test_show_add_forum_button_for_superuser_if_forum_is_category_type(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        url = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug})

        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertNotContains(
            response, reverse("forum_extension:create_subcategory", kwargs={"pk": forum.pk}), status_code=200
        )

        user.is_superuser = True
        user.save()
        response = self.client.get(url)
        self.assertContains(
            response, reverse("forum_extension:create_subcategory", kwargs={"pk": forum.pk}), status_code=200
        )

    def test_siblings_in_context(self):
        forum = CategoryForumFactory(with_public_perms=True)
        ForumFactory.create_batch(3, parent=forum, with_public_perms=True)
        child_forum = forum.get_children().first()
        url = reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data["sibling_forums"].count(), 3)
        for f in forum.get_children():
            self.assertContains(response, f.name)

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
            f'div class="dropdown-menu dropdown-menu-end" aria-labelledby="dropdownMenuSocialShare{child_forum.id}">',
            status_code=200,
        )

    def test_upvote_actions(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()

        # anonymous
        anonymous_html = (
            '<a href="/inclusion_connect/authorize?next=%2Fforum%2F'
            f'{child_forum.slug}-{child_forum.pk}%2F%23{child_forum.pk}"'
            ' rel="nofollow"'
            ' class="btn btn-sm btn-ico-only btn-link btn-secondary" data-bs-toggle="tooltip" data-bs-placement="top"'
            ' title="Connectez-vous pour sauvegarder">'
            ' <i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>0</span>'
        )
        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(response, anonymous_html, status_code=200, html=True)

        # authenticated
        self.client.force_login(self.user)
        no_upvote_html = (
            '<button type="submit"'
            ' title="Sauvegarder"'
            ' class="btn btn-sm btn-ico btn-secondary matomo-event px-2"'
            ' data-matomo-category="engagement"'
            ' data-matomo-action="upvote"'
            ' data-matomo-option="post"'
            " >"
            ' <i class="ri-bookmark-line me-1" aria-hidden="true"></i>'
            "<span>0</span>"
        )
        response = self.client.get(reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": forum.slug}))
        self.assertContains(response, no_upvote_html, status_code=200, html=True)

        child_forum.upvotes.create(voter=self.user)
        upvoted_html = (
            '<button type="submit"'
            ' title="Sauvegarder"'
            ' class="btn btn-sm btn-ico btn-secondary matomo-event px-2"'
            ' data-matomo-category="engagement"'
            ' data-matomo-action="upvote"'
            ' data-matomo-option="post"'
            " >"
            ' <i class="ri-bookmark-fill me-1" aria-hidden="true"></i>'
            "<span>1</span>"
        )
        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(response, upvoted_html, status_code=200, html=True)

    def test_upvotes_count(self):
        forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        child_forum = forum.get_children().first()

        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(
            response, '<i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>0</span>', status_code=200
        )

        child_forum.upvotes.create(voter=self.user)

        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(
            response, '<i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>1</span>', status_code=200
        )

        child_forum.upvotes.create(voter=UserFactory())

        response = self.client.get(
            reverse("forum_extension:forum", kwargs={"pk": child_forum.pk, "slug": child_forum.slug})
        )
        self.assertContains(
            response, '<i class="ri-bookmark-line me-1" aria-hidden="true"></i><span>2</span>', status_code=200
        )

    def test_can_view_update_forum_link(self):
        url = reverse("forum_extension:edit_forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug})
        response = self.client.get(self.url)
        self.assertNotContains(response, url)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertNotContains(response, url)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertNotContains(response, url)

        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertContains(response, url)

    def test_filtered_queryset_on_tag(self):
        tag = faker.word()
        topic = TopicFactory(forum=self.forum, with_tags=[tag], with_post=True)

        with self.assertNumQueries(20):
            response = self.client.get(
                reverse("forum_extension:forum", kwargs={"pk": self.forum.pk, "slug": self.forum.slug}), {"tags": tag}
            )
        self.assertContains(response, topic.subject)
        self.assertNotContains(response, self.topic.subject)

    def test_queryset_for_unanswered_topics(self):
        PostFactory(topic=self.topic)
        response = self.client.get(self.url + f"?filter={Filters.NEW.value}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["paginator"].count, 0)
        self.assertEqual(response.context_data["active_filter_name"], Filters.NEW.label)

        new_topic = TopicFactory(with_post=True, forum=self.forum)

        response = self.client.get(self.url + f"?filter={Filters.NEW.value}")
        self.assertEqual(response.context_data["paginator"].count, 1)
        self.assertContains(response, new_topic.subject, status_code=200)
        self.assertEqual(response.context_data["active_filter_name"], Filters.NEW.label)

        for topic in Topic.objects.exclude(id=new_topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

    def test_queryset_for_certified_topics(self):
        response = self.client.get(self.url + f"?filter={Filters.CERTIFIED.value}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["paginator"].count, 0)
        self.assertEqual(response.context_data["active_filter_name"], Filters.CERTIFIED.label)

        certified_topic = TopicFactory(with_post=True, with_certified_post=True, forum=self.forum)
        TopicFactory(
            with_post=True,
            with_certified_post=True,
            forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM, with_public_perms=True),
        )

        response = self.client.get(self.url + f"?filter={Filters.CERTIFIED.value}")
        self.assertEqual(response.context_data["paginator"].count, 1)
        self.assertContains(response, certified_topic.subject, status_code=200)
        self.assertContains(response, certified_topic.certified_post.post.content.raw[:100])
        self.assertEqual(response.context_data["active_filter_name"], Filters.CERTIFIED.label)

        for topic in Topic.objects.exclude(id=certified_topic.id):
            with self.subTest(topic):
                self.assertNotContains(response, topic.subject)

    def test_banner_display_on_subcategory_forum(self):
        category_forum = CategoryForumFactory(with_child=True, with_public_perms=True)
        forum = category_forum.get_children().first()
        response = self.client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        self.assertContains(response, forum.image.url.split("=")[0])


class TestForumViewContent:
    def test_not_rated_forum(self, client, db, snapshot):
        category_forum = CategoryForumFactory(with_public_perms=True, with_child=True, name="B Category")
        forum = category_forum.get_children().first()

        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="#rating-area1", replace_in_href=[category_forum, forum])
        assert str(content) == snapshot(name="not_rated_forum")

    def test_rated_forum(self, client, db, snapshot):
        client.session.save()
        category_forum = CategoryForumFactory(with_public_perms=True, with_child=True)
        forum = category_forum.get_children().first()
        ForumRatingFactory(forum=forum, rating=5, session_id=client.session.session_key)

        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="#rating-area1")
        assert str(content) == snapshot(name="rated_forum")


reset_forum_sequence = pytest.fixture(reset_model_sequence_fixture(Forum))


@pytest.fixture(name="documentation_forum")
def documentation_forum_fixture():
    return ForumFactory(
        parent=CategoryForumFactory(with_public_perms=True, name="Parent-Forum"),
        with_public_perms=True,
        with_image=True,
        for_snapshot=True,
    )


class TestDocumentationForumContent:
    def test_documentation_forum_share_actions(self, client, db, snapshot, reset_forum_sequence, documentation_forum):
        response = client.get(documentation_forum.get_absolute_url())
        content = parse_response_to_soup(response)

        upvotes_area = content.select(f"#upvotesarea{str(documentation_forum.pk)}")[0]
        assert str(upvotes_area) == snapshot(name="template_documentation_upvotes")
        social_share_area = content.select(f"#dropdownMenuSocialShare{str(documentation_forum.pk)}")[0]
        assert str(social_share_area) == snapshot(name="template_documentation_social_share")

    def test_documentation_forum_header_content(self, client, db, snapshot, reset_forum_sequence, documentation_forum):
        sibling_forum = ForumFactory(parent=documentation_forum.parent, with_public_perms=True, name="Test-2")

        response = client.get(documentation_forum.get_absolute_url())
        content = parse_response_to_soup(response)

        assert len(content.find_all("img", src=re.compile(documentation_forum.image.name))) == 1
        assert (
            len(
                content.select(
                    "div.textarea_cms_md", string=(lambda x: x.startswith(str(documentation_forum.description)[:10]))
                )
            )
            == 1
        )

        user_add_topic = content.find_all(
            "a",
            href=str(
                reverse("forum_conversation:topic_create", args=(documentation_forum.slug, documentation_forum.pk))
            ),
        )
        assert len(user_add_topic) == 2

        link_to_parent = content.find_all("a", href=documentation_forum.parent.get_absolute_url())
        assert len(link_to_parent) == 1
        assert (str(link_to_parent[0])) == snapshot(name="template_documentation_link_to_parent")

        assert len(content.find_all("a", href=sibling_forum.get_absolute_url())) == 1


@pytest.fixture(name="discussion_area_forum")
def discussion_area_forum_fixture():
    return ForumFactory(with_public_perms=True, name="A Forum")


class TestBreadcrumb:
    def test_sub_discussion_area_forum(self, client, db, snapshot, discussion_area_forum):
        forum = ForumFactory(parent=discussion_area_forum, with_public_perms=True, name="b")
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="nav.c-breadcrumb")
        assert str(content) == snapshot(name="sub_discussion_area_forum")

    def test_forum(self, client, db, snapshot, discussion_area_forum):
        forum = ForumFactory(with_public_perms=True)
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="nav.c-breadcrumb")
        assert str(content) == snapshot(name="forum")

    def test_sub_forum(self, client, db, snapshot, discussion_area_forum):
        parent_forum = ForumFactory(with_public_perms=True, name="B Forum")
        forum = ForumFactory(parent=parent_forum, with_public_perms=True)
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="nav.c-breadcrumb", replace_in_href=[parent_forum])
        assert str(content) == snapshot(name="sub_forum")

    def test_category_forum(self, client, db, snapshot, discussion_area_forum):
        forum = CategoryForumFactory(with_public_perms=True)
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="nav.c-breadcrumb")
        assert str(content) == snapshot(name="category_forum")

    def test_child_category_forum(self, client, db, snapshot, discussion_area_forum):
        parent_forum = CategoryForumFactory(with_child=True, with_public_perms=True, name="A Category")
        forum = parent_forum.get_children().first()
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="nav.c-breadcrumb", replace_in_href=[parent_forum])
        assert str(content) == snapshot(name="child_category_forum")

    def test_grandchild_category_forum(self, client, db, snapshot, discussion_area_forum):
        parent_forum = CategoryForumFactory(with_public_perms=True, with_child=True, name="B Category")
        forum = ForumFactory(parent=parent_forum.get_children().first(), with_public_perms=True)
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(
            response,
            selector="nav.c-breadcrumb",
            replace_in_href=[parent_forum, parent_forum.get_children().first()],
        )
        assert str(content) == snapshot(name="grandchild_category_forum")

    def test_newsfeed_forum(self, client, db, snapshot, discussion_area_forum):
        forum = ForumFactory(kind="NEWS", with_public_perms=True)
        response = client.get(reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="nav.c-breadcrumb")
        assert str(content) == snapshot(name="newsfeed_forum")
