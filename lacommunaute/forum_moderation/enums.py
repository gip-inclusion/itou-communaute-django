from enum import Enum


class BlockedPostReason(Enum):
    HTML_TAGS = "HTML tags detected"
    ALTERNATIVE_LANGUAGE = "Alternative Language detected"
    BLOCKED_DOMAIN = "Blocked Domain detected"
    BLOCKED_USER = "Blocked Email detected"
    MODERATOR_DISAPPROVAL = "Moderator disapproval"

    @classmethod
    def reasons_tracked_for_stats(cls):
        """
        We store BlockedPost objects for posts which are of interest for review
        The list of "reasons for interest" are returned by this function
        """
        return [
            cls.ALTERNATIVE_LANGUAGE.value,
            cls.BLOCKED_DOMAIN.value,
            cls.BLOCKED_USER.value,
            cls.MODERATOR_DISAPPROVAL.value,
        ]
