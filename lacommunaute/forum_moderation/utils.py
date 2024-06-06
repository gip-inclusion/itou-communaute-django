from enum import Enum

from django.conf import settings
from langdetect import detect
from machina.models.fields import render_func
from markdown2 import Markdown

from lacommunaute.forum_moderation.models import BlockedDomainName, BlockedEmail


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


def check_post_approbation(post):
    """
    Check if a post should be approved or not
    Force markdown rendering to check for HTML tags
    because the post is not save yet
    """
    rendered = render_func(post.content.raw, safe_mode=True)

    conditions = [
        (
            post.username and BlockedDomainName.objects.filter(domain=post.username.split("@")[-1]).exists(),
            BlockedPostReason.BLOCKED_DOMAIN.value,
        ),
        (Markdown.html_removed_text_compat in rendered, BlockedPostReason.HTML_TAGS.value),
        (detect(post.content.raw) not in settings.LANGUAGE_CODE, BlockedPostReason.ALTERNATIVE_LANGUAGE.value),
        (
            post.username and BlockedEmail.objects.filter(email=post.username).exists(),
            BlockedPostReason.BLOCKED_USER.value,
        ),
    ]
    post.approved, post.update_reason = next(
        ((not condition, reason) for condition, reason in conditions if condition), (post.approved, post.update_reason)
    )

    return post
