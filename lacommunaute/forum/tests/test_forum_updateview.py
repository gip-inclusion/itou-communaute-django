from io import BytesIO

import pytest  # noqa
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from faker import Faker
from PIL import Image
from pytest_django.asserts import assertContains

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.users.factories import UserFactory


@pytest.fixture
def fake_image():
    fake = Faker()
    image_name = fake.pystr(min_chars=30, max_chars=40, prefix="pytest_", suffix=".png")

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
    assert response.status_code == 403

    user.is_superuser = True
    user.save()
    response = client.get(url)
    assert response.status_code == 200


def test_context_data(client, db):
    client.force_login(UserFactory(is_superuser=True))
    forum = ForumFactory()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    assertContains(response, f"Mettre à jour le forum {forum.name}", html=True)
    assertContains(response, reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))


def test_update_forum_image(client, db, fake_image):
    client.force_login(UserFactory(is_superuser=True))
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
