from django.conf import settings
from langdetect import detect
from markdown2 import Markdown

from lacommunaute.forum_moderation.models import BlockedDomainName, BlockedEmail


def check_post_approbation(post):
    """
    Check if a post should be approved or not
    """

    conditions = [
        (
            post.username and BlockedDomainName.objects.filter(domain=post.username.split("@")[-1]).exists(),
            "Blocked Domain detected",
        ),
        (Markdown.html_removed_text_compat in post.content.rendered, "HTML tags detected"),
        (detect(post.content.raw) not in settings.LANGUAGE_CODE, "Alternative Language detected"),
        (post.username and BlockedEmail.objects.filter(email=post.username).exists(), "Blocked Email detected"),
    ]
    post.approved, post.update_reason = next(
        ((not condition, reason) for condition, reason in conditions if condition), (post.approved, post.update_reason)
    )

    return post
