from datetime import datetime

from django.utils.timezone import now, timedelta
from django.utils.translation import gettext_lazy as _

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.users.models import User


def last_notification(kind=None) -> datetime:
    return getattr(EmailSentTrack.objects.filter(kind=kind).last(), "created", now() - timedelta(days=5))


def collect_new_users_for_onboarding():
    return User.objects.filter(date_joined__gte=last_notification(kind=EmailSentTrackKind.ONBOARDING)).order_by(
        "date_joined"
    )


def get_serialized_messages(notifications, action_verb=_("responded to")):
    return [
        {
            "poster": n.post.poster_display_name,
            "action": f"{action_verb} '{n.post.subject}'",
            "forum": n.post.topic.forum.name,
            "url": n.post.topic.get_absolute_url(with_fqdn=True),
        }
        for n in notifications
    ]
