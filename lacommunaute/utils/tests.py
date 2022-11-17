from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.utils.encoding import force_bytes
from machina.test.factories.attachments import AttachmentFactory
from machina.test.factories.conversation import PostFactory, create_topic
from machina.test.factories.forum import create_forum

from lacommunaute.users.factories import UserFactory


class AttachmentsTemplateTagTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        poster = UserFactory()
        cls.post = PostFactory(topic=create_topic(forum=create_forum(), poster=poster), poster=poster)

    @override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
    def test_is_an_image(self):
        for filename in ["test.png", "test.jpg", "test.JPG", "test.jpeg", "test.JPEG"]:
            with self.subTest(filename=filename):
                f = SimpleUploadedFile(filename, force_bytes("file_content"))
                attachment = AttachmentFactory(post=self.post, file=f)

                out = Template("{% load attachments_tags %}" "{{ attachment|is_image }}").render(
                    Context(
                        {
                            "attachment": attachment,
                        }
                    )
                )
                self.assertEqual(out, "True")

    @override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
    def test_is_not_an_image(self):
        for filename in ["test.csv", "test.xlsx", "test.pdf", "test.html"]:
            with self.subTest(filename=filename):
                f = SimpleUploadedFile(filename, force_bytes("file_content"))
                attachment = AttachmentFactory(post=self.post, file=f)

                out = Template("{% load attachments_tags %}" "{{ attachment|is_image }}").render(
                    Context(
                        {
                            "attachment": attachment,
                        }
                    )
                )
                self.assertEqual(out, "False")


class SettingsContextProcessorsTest(TestCase):
    @override_settings(ALLOWED_HOSTS=["allowed.com"])
    def test_disallowed_host(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(hasattr(response.wsgi_request, "htmx"))

    def test_allowed_host(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.wsgi_request, "htmx"))

    def test_htmx_request(self):
        headers = {"HX-Request": True}
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.wsgi_request, "htmx"))
        self.assertEqual(response.status_code, 405)
