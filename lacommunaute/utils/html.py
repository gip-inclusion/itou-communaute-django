import re


def wrap_iframe_in_div_tag(text):
    # iframe tags must be wrapped in a div tag to be displayed correctly
    # add div tag if not present

    iframe_regex = r"((<div>)?<iframe.*?</iframe>(</div>)?)"

    for match, starts_with, ends_with in re.findall(iframe_regex, text, re.DOTALL):
        if not starts_with and not ends_with:
            text = text.replace(match, f"<div>{match}</div>")

    return text
