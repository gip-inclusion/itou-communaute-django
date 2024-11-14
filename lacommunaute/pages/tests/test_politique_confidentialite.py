from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed


def test_template(client, db):
    response = client.get(reverse("pages:politique_de_confidentialite"))
    assertTemplateUsed(response, "pages/politique_de_confidentialite.html")
