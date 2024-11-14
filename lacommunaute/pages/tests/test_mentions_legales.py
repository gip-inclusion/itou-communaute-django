from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


def test_template(client, db):
    response = client.get(reverse("pages:mentions_legales"))
    assertTemplateUsed(response, "pages/mentions_legales.html")
