"""
https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
"""
from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe


"""
This template tags have for goal to mutualize all the dependencies and specifics component from the itou theme.

To use it, you need to copy (if it's not already done) the folder `dist` of https://github.com/betagouv/itou-theme
And you need to paste it into the folder `itou/static/vendor/theme-inclusion`
"""

register = template.Library()

URL_THEME = "vendor/theme-inclusion/"

CSS_DEPENDENCIES_THEME = [
    {
        "is_external": False,
        "src": "stylesheets/app.css",
    },
]


JS_DEPENDENCIES_THEME = [
    {
        "is_external": True,
        "src": "https://cdn.jsdelivr.net/npm/jquery@3.6.1/dist/jquery.min.js",
        "integrity": "sha256-o88AwQnZB+VDvE9tvIXrMQaPlFFSUTR+nldQm1LuPXQ=",
    },
    {
        "is_external": True,
        "src": "https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js",
        "integrity": "sha256-/ijcOLwFf26xEYAjW75FizKVo5tnTYiQddPZoLUHHZ8=",
    },
    {
        "is_external": True,
        "src": "https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.min.js",
        "integrity": "sha256-QjIXq/h3XOotww+h/j4cXiTcNZqA8cN60pqGCUv+gdE=",
    },
    {
        "is_external": False,
        "src": "javascripts/app.js",
    },
]


@register.simple_tag
def static_theme(url_path):
    """
    Usage:
        {% load theme_inclusion %}
        {% static_theme url_path %}
    """
    static_path = "{base_url}{url_path}".format(base_url=URL_THEME, url_path=url_path)
    return static(static_path)


@register.simple_tag
def static_theme_images(url_path):
    """
    Usage:
        {% load theme_inclusion %}
        {% static_theme_images url_path %}
    """
    static_path = "{base_url}images/{url_path}".format(base_url=URL_THEME, url_path=url_path)
    return static(static_path)


@register.simple_tag
def import_static_CSS_theme_inclusion():
    scripts_import = ""
    for css_dep in CSS_DEPENDENCIES_THEME:
        if css_dep["is_external"]:
            scripts_import += (
                '<link rel="stylesheet" href="{}" integrity="{}" ' 'crossorigin="anonymous" type="text/css">'
            ).format(css_dep["src"], css_dep["integrity"])
        else:
            scripts_import += '<link rel="stylesheet" href="{}" type="text/css">'.format(static_theme(css_dep["src"]))
    return mark_safe(scripts_import)


@register.simple_tag
def import_static_JS_theme_inclusion():
    scripts_import = ""
    for js_dep in JS_DEPENDENCIES_THEME:
        if js_dep["is_external"]:
            scripts_import += '<script src="{}" integrity="{}" crossorigin="anonymous"></script>'.format(
                js_dep["src"], js_dep["integrity"]
            )
        else:
            scripts_import += '<script src="{}"></script>'.format(static_theme(js_dep["src"]))
    return mark_safe(scripts_import)
