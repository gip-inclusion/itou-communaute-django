from django.conf import settings
from langdetect import LangDetectException, detect
from langdetect.detector import Detector
from machina.models.fields import render_func
from markdown2 import Markdown

from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.models import BlockedDomainName, BlockedEmail


def check_post_approbation(post):
    """
    Check if a post should be approved or not
    Force markdown rendering to check for HTML tags
    because the post is not save yet
    """
    rendered = render_func(post.content.raw, safe_mode=True)
    try:
        language = detect(post.content.raw)
    except LangDetectException:
        language = Detector.UNKNOWN_LANG

    conditions = [
        (
            post.username and BlockedDomainName.objects.filter(domain=post.username.split("@")[-1]).exists(),
            BlockedPostReason.BLOCKED_DOMAIN.label,
        ),
        (Markdown.html_removed_text_compat in rendered, BlockedPostReason.HTML_TAGS.label),
        (language not in settings.LANGUAGE_CODE, BlockedPostReason.ALTERNATIVE_LANGUAGE.label),
        (
            post.username and BlockedEmail.objects.filter(email=post.username).exists(),
            BlockedPostReason.BLOCKED_USER.label,
        ),
    ]
    post.approved, post.update_reason = next(
        ((not condition, reason) for condition, reason in conditions if condition), (post.approved, post.update_reason)
    )

    return post
