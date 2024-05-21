from django.core.exceptions import ValidationError


def validate_image_size(value):
    max_size = 1024 * 1024 * 5

    if value.size > max_size:
        raise ValidationError("L'image ne doit pas dépasser 5 Mo")
