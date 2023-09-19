from mimetypes import guess_type

from django import template


register = template.Library()


@register.filter
def is_image(object):
    content_type, _ = guess_type(object.file.name)
    if content_type in ["image/png", "image/jpeg"]:
        return True
    else:
        return False


@register.filter
def is_available(object):
    return object.file.field.storage.exists(object.file.name)
