from datetime import datetime

from django.utils.timezone import now, timedelta

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.users.models import User


def last_notification(kind=None) -> datetime:
    return getattr(EmailSentTrack.objects.filter(kind=kind).last(), "created", now() - timedelta(days=5))


def collect_new_users_for_onboarding():
    return User.objects.filter(date_joined__gte=last_notification(kind=EmailSentTrackKind.ONBOARDING)).order_by(
        "date_joined"
    )


def get_serialized_messages(notifications):
    return [
        {
            "poster": n.post.poster_display_name,
            "action": (
                "a posé une nouvelle question" if n.post.is_topic_head else f"a répondu à '{n.post.topic.subject}'"
            ),
            "forum": n.post.topic.forum.name,
            "url": n.post.topic.get_absolute_url(with_fqdn=True),
        }
        for n in notifications
    ]
