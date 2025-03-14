from io import BytesIO

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from PIL import Image
from pytest_django.asserts import assertContains
from taggit.models import Tag

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum.forms import SubCategoryForumUpdateForm
from lacommunaute.partner.factories import PartnerFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup, reset_model_sequence_fixture


faker = Faker(settings.LANGUAGE_CODE)

reset_tag_sequence = pytest.fixture(reset_model_sequence_fixture(Tag))


@pytest.fixture
def fake_image():
    fake = Faker()
    image_name = fake.pystr(min_chars=30, max_chars=40, prefix="pytest_", suffix=".jpg")

    image = Image.new("RGB", (100, 100))
    image_file = BytesIO()
    image.save(image_file, format="JPEG")
    image_file.seek(0)
    uploaded_image = SimpleUploadedFile(image_name, image_file.read(), content_type="image/jpeg")

    yield uploaded_image


def test_user_access(client, db):
    forum = ForumFactory()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    assert response.status_code == 302

    user = UserFactory()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 403

    user.is_staff = True
    user.save()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "forum,should_be_subcategoryupdateform",
    [
        (lambda: ForumFactory(), False),
        (lambda: CategoryForumFactory(), False),
        (lambda: CategoryForumFactory(with_child=True).get_children().first(), True),
    ],
)
def test_context_data(client, db, forum, should_be_subcategoryupdateform):
    client.force_login(UserFactory(is_in_staff_group=True))
    forum = forum()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    assertContains(response, f"Mettre à jour le forum {forum.name}", html=True)
    assertContains(response, reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
    assert isinstance(response.context["form"], SubCategoryForumUpdateForm) == should_be_subcategoryupdateform


def test_update_forum_image(client, db, fake_image):
    client.force_login(UserFactory(is_in_staff_group=True))
    forum = CategoryForumFactory(with_child=True).get_children().first()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})

    response = client.post(
        url,
        data={
            "name": "new name",
            "short_description": "new short description",
            "description": "new description",
            "image": fake_image,
        },
    )
    assert response.status_code == 302

    forum.refresh_from_db()
    assert forum.name == "new name"
    assert forum.short_description == "new short description"
    assert forum.description.raw == "new description"
    assert forum.image.name == fake_image.name


def test_update_subcategory_forum_parent(client, db):
    forum = CategoryForumFactory(with_child=True).get_children().first()
    new_parent = CategoryForumFactory()
    client.force_login(UserFactory(is_in_staff_group=True))

    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.post(
        url,
        data={
            "name": forum.name,
            "short_description": forum.short_description,
            "description": forum.description.raw,
            "parent": new_parent.pk,
        },
    )
    assert response.status_code == 302

    forum.refresh_from_db()
    assert forum.parent == new_parent


def test_certified_forum(client, db):
    client.force_login(UserFactory(is_in_staff_group=True))
    forum = CategoryForumFactory(with_child=True).get_children().first()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})

    response = client.post(
        url,
        data={
            "name": "new name",
            "short_description": "new short description",
            "description": "new description",
            "certified": True,
        },
    )
    assert response.status_code == 302

    forum.refresh_from_db()
    assert forum.certified is True


def test_selected_tags_are_preloaded(client, db, reset_tag_sequence, snapshot):
    client.force_login(UserFactory(is_in_staff_group=True))
    forum = ForumFactory(with_tags=["iae", "siae", "prescripteur"])
    Tag.objects.create(name="undesired_tag")
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})

    response = client.get(url)
    assert response.status_code == 200

    content_tags = parse_response_to_soup(
        response, selector="#div_id_tags", replace_in_href=[tag for tag in Tag.objects.all()]
    )
    assert str(content_tags) == snapshot(name="selected_tags_preloaded")


def test_added_tags_are_saved(client, db):
    client.force_login(UserFactory(is_in_staff_group=True))
    forum = ForumFactory()

    Tag.objects.bulk_create([Tag(name=tag, slug=tag) for tag in [faker.word() for _ in range(3)]])
    tags_list = [faker.word() for i in range(2)]

    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.post(
        url,
        data={
            "name": forum.name,
            "short_description": forum.short_description,
            "description": forum.description.raw,
            "tags": [Tag.objects.first().pk],
            "new_tags": ", ".join(tags_list),
        },
    )

    assert response.status_code == 302

    forum.refresh_from_db()
    assert all(tag in [tag.name for tag in forum.tags.all()] for tag in [Tag.objects.first().name] + tags_list)


def test_update_forum_without_tag(client, db):
    client.force_login(UserFactory(is_in_staff_group=True))
    forum = ForumFactory()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.post(
        url,
        data={
            "name": forum.name,
            "short_description": forum.short_description,
            "description": forum.description.raw,
        },
    )
    assert response.status_code == 302

    forum.refresh_from_db()
    assert forum.tags.count() == 0


@pytest.mark.parametrize(
    "initial_partner,post_partner",
    [
        (lambda: None, lambda: None),
        (lambda: None, lambda: PartnerFactory()),
        (lambda: PartnerFactory(), lambda: None),
        (lambda: PartnerFactory(), lambda: PartnerFactory()),
    ],
)
def test_select_partner(client, db, initial_partner, post_partner):
    initial_partner = initial_partner()
    post_partner = post_partner()
    forum = ForumFactory(partner=initial_partner)
    client.force_login(UserFactory(is_in_staff_group=True))

    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.post(
        url,
        data={
            "name": forum.name,
            "short_description": forum.short_description,
            "description": forum.description.raw,
            "partner": post_partner.id if post_partner else "",
        },
    )
    assert response.status_code == 302

    forum.refresh_from_db()
    assert forum.partner == post_partner
