from django.conf import settings
from django.utils.timezone import now, timedelta

from lacommunaute.forum_conversation.models import Post
from lacommunaute.notification.models import EmailSentTrack


def last_notification(kind=None):
    return getattr(EmailSentTrack.objects.filter(kind=kind).last(), "created", now() - timedelta(days=1))


def collect_first_replies():
    return [
        (
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{post.topic.get_absolute_url()}",
            post.topic.subject,
            post.topic.poster_email,
            post.poster_display_name,
        )
        for post in Post.objects.filter(
            created__gte=last_notification(),
            approved=True,
        )
        if post.position == 2
    ]
