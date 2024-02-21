from datetime import datetime

from django.utils.timezone import now, timedelta

from lacommunaute.forum_conversation.models import Topic
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.users.models import User


def last_notification(kind=None) -> datetime:
    return getattr(EmailSentTrack.objects.filter(kind=kind).last(), "created", now() - timedelta(days=5))


def collect_first_replies():
    return [
        (
            topic.get_absolute_url(with_fqdn=True),
            topic.subject,
            topic.mails_to_notify(),
            topic.last_post.poster_display_name,
        )
        for topic in Topic.objects.with_first_reply(last_notification(kind=EmailSentTrackKind.FIRST_REPLY))
    ]


def collect_following_replies():
    return [
        (
            topic.get_absolute_url(with_fqdn=True),
            topic.subject,
            topic.mails_to_notify(),
            f"{topic.new_replies} nouvelle réponse"
            if topic.new_replies == 1
            else f"{topic.new_replies} nouvelles réponses",
        )
        for topic in Topic.objects.with_following_replies(last_notification(kind=EmailSentTrackKind.FOLLOWING_REPLIES))
    ]


def collect_new_users_for_onboarding():
    return User.objects.filter(date_joined__gte=last_notification(kind=EmailSentTrackKind.ONBOARDING)).order_by(
        "date_joined"
    )
