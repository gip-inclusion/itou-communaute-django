from django.test import TestCase

from lacommunaute.users.factories import DEFAULT_PASSWORD, UserFactory
from lacommunaute.www.users.forms import SignUpForm


class SignUpFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_required_fields(self):
        form = SignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("Ce champ est obligatoire.", form.errors["email"])
        self.assertIn("Ce champ est obligatoire.", form.errors["password"])

    def test_email_exists(self):
        form_data = {
            "email": self.user.email,
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("That email is already taken", form.errors["email"])

    def test_signup_ok(self):
        form_data = {
            "email": "test@test.com",
            "password": DEFAULT_PASSWORD,
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())
