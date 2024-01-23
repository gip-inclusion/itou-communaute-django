import importlib

from bs4 import BeautifulSoup
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


def parse_response_to_soup(response, selector=None, no_html_body=False, replace_in_href=None):
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
            replacement
            if isinstance(replacement, tuple)
            else (str(replacement.pk), f"[PK of {type(replacement).__name__}]")
            for replacement in replace_in_href
        ]
        for links in soup.find_all(attrs={"href": True}):
            [links.attrs.update({"href": links.attrs["href"].replace(*replacement)}) for replacement in replacements]
    return soup
