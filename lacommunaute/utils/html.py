import re


def wrap_iframe_in_div_tag(text):
    """
    given a markdown text, wrap all iframe tags in a div tag
    this is required for iframes to be displayed correctly
    """

    iframe_regex = r"((<div>)?(<iframe[^>]*><\/iframe>)(<\/div>)?)"

    for match, starts_with, iframe, ends_with in re.findall(iframe_regex, text):
        if not (starts_with and ends_with):
            text = text.replace(match, f"<div>{iframe}</div>")

    return text
