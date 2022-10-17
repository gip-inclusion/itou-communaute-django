from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.users.models import User


PASSWORD = "password"


class ManagerTest(TestCase):
    def test_create_user(self):
        User.objects.create_user(email="user@beta.gouv.fr", password=PASSWORD)
        user = User.objects.get(email="user@beta.gouv.fr")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User.objects.create_superuser(email="superuser@beta.gouv.fr", password=PASSWORD)
        user = User.objects.get(email="superuser@beta.gouv.fr")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class ModelTest(TestCase):
    def test_email_is_unique(self):
        User.objects.create_user(email="user@beta.gouv.fr", password=PASSWORD)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="user@beta.gouv.fr", password=PASSWORD)
