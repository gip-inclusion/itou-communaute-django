from django.db import models


class BlockedPostReason(models.TextChoices):
    HTML_TAGS = "HTML_TAGS", "HTML tags detected"
    ALTERNATIVE_LANGUAGE = "ALTERNATIVE_LANGUAGE", "Alternative Language detected"
    BLOCKED_DOMAIN = "BLOCKED_DOMAIN", "Blocked Domain detected"
    BLOCKED_USER = "BLOCKED_USER", "Blocked Email detected"
    MODERATOR_DISAPPROVAL = "MODERATOR_DISAPPROVAL", "Moderator disapproval"

    @classmethod
    def reasons_tracked_for_stats(cls):
        """
        We store BlockedPost objects for posts which are of interest for review
        The list of "reasons for interest" are returned by this function
        """
        return [
            cls.ALTERNATIVE_LANGUAGE,
            cls.BLOCKED_DOMAIN,
            cls.BLOCKED_USER,
            cls.MODERATOR_DISAPPROVAL,
        ]
