from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from lacommunaute.users.factories import DEFAULT_PASSWORD, UserFactory
from lacommunaute.users.models import User


class SignUpViewTest(TestCase):
    def setUp(self) -> None:
        self.email = "signup@beta.gouv.fr"
        self.url = reverse("users:signup")

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_signup_not_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.email,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=self.email)

    def test_signup_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.email,
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
            "first_name": "John",
            "last_name": "Woo",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse("pages:home"), status_code=302)
        self.assertIsNotNone(User.objects.get(email=self.email))


class PasswordResetViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("users:password_reset")

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_email_sent(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.user.email,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:password_reset_done"),
        )

        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]

        token = response.context.get("token")
        uid = response.context.get("uid")
        password_reset_token_url = reverse(
            "users:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        self.assertIn(password_reset_token_url, email.body)
        self.assertEqual(
            [
                self.user.email,
            ],
            email.to,
        )

    def test_unknown_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": "unknown.email@beta.gouv.fr",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:password_reset_done"),
        )

        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneViewTest(TestCase):
    def test_rendered_page(self):
        response = self.client.get(reverse("users:password_reset_done"))
        self.assertEqual(response.status_code, 200)


class PasswordResetConfirmViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))  # .decode()
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse(
            "users:password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )

    def test_csrf(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_token(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "new_password1": DEFAULT_PASSWORD + "1",
            "new_password2": DEFAULT_PASSWORD + "1",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()

    def test_invalid_token(self):
        """
        invalidate the token by changing the password
        """
        self.user.set_password("abcdef123")
        self.user.save()

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Le lien de réinitialisation du mot de passe n'est pas valide"
        )


class PasswordResetCompleteViewTest(TestCase):
    def test_rendered_page(self):
        response = self.client.get(reverse("users:password_reset_complete"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("users:login"))
