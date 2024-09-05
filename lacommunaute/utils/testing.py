import importlib

from bs4 import BeautifulSoup
from django.db import connection
from django.test.utils import TestContextDecorator


class reload_module(TestContextDecorator):
    def __init__(self, module):
        self._module = module
        self._original_values = {key: getattr(module, key) for key in dir(module) if not key.startswith("__")}
        super().__init__()

    def enable(self):
        importlib.reload(self._module)

    def disable(self):
        for key, value in self._original_values.items():
            setattr(self._module, key, value)


def parse_response_to_soup(response, selector=None, no_html_body=False, replace_in_href=None, replace_img_src=False):
    soup = BeautifulSoup(response.content, "html5lib", from_encoding=response.charset or "utf-8")
    if no_html_body:
        # If the provided HTML does not contain <html><body> tags
        # html5lib will always add them around the response:
        # ignore them
        soup = soup.body
    if selector is not None:
        [soup] = soup.select(selector)
    for csrf_token_input in soup.find_all("input", attrs={"name": "csrfmiddlewaretoken"}):
        csrf_token_input["value"] = "NORMALIZED_CSRF_TOKEN"
    if "nonce" in soup.attrs:
        soup["nonce"] = "NORMALIZED_CSP_NONCE"
    for csp_nonce_script in soup.find_all("script", {"nonce": True}):
        csp_nonce_script["nonce"] = "NORMALIZED_CSP_NONCE"
    if replace_in_href:
        replacements = [
            (
                replacement
                if isinstance(replacement, tuple)
                else (str(replacement.pk), f"[PK of {type(replacement).__name__}]")
            )
            for replacement in replace_in_href
        ]
        for attr in ["href", "hx-post", "hx-get"]:
            for links in soup.find_all(attrs={attr: True}):
                [links.attrs.update({attr: links.attrs[attr].replace(*replacement)}) for replacement in replacements]
    if replace_img_src:
        for attr in ["src"]:
            for links in soup.find_all("img", attrs={attr: True}):
                links.attrs.update({attr: "[img src]"})
    return soup


def reset_model_sequence_fixture(*model_classes):
    """
    :return: a function which can adjust and reset a primary key sequence for use as a pytest fixture
    it is used to temporarily change the primary key, so that it is predictable (e.g. for snapshots)
    """

    def reset_model_sequence():
        def set_sequence_value(cursor, value):
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence(%s, 'id'), %s, false);", (model_class._meta.db_table, str(value))
            )

        with connection.cursor() as cursor:
            for model_class in model_classes:
                set_sequence_value(cursor, 9999)

    return reset_model_sequence
