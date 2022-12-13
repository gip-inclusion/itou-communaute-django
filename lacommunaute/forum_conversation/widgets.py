from django.forms.widgets import Textarea


class MarkdownTextareaWidget(Textarea):
    """A simple Textarea widget using the easymde JS library to provide Markdown editor."""

    class Media:
        css = {
            "all": ("machina/build/css/vendor/easymde.min.css",),
        }
        js = (
            "machina/build/js/vendor/easymde.min.js",
            "machina/build/js/machina.editor.min.js",
        )

    def render(self, name, value, attrs=None, **kwargs):
        # removed classes attributes, to hide widget toolbar
        return super().render(name, value, attrs, **kwargs)
