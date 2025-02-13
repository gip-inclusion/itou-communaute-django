from datetime import datetime

from django.utils.timezone import now, timedelta

from lacommunaute.notification.enums import EmailSentTrackKind, delay_of_notifications
from lacommunaute.notification.models import EmailSentTrack, Notification
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
            "url": f"{n.post.topic.get_absolute_url(with_fqdn=True)}?notif={n.uuid}",
        }
        for n in notifications
    ]


def create_post_notifications(post):
    """
    When a Post is created, we schedule notifications to users active in the thread
    """
    # NOTE: notifications solution depends on the fact that approval is completed at the time of creation
    if not post.approved:
        return

    if post.is_topic_head:
        kind = EmailSentTrackKind.PENDING_TOPIC
    elif post.is_first_reply:
        kind = EmailSentTrackKind.FIRST_REPLY
    else:
        kind = EmailSentTrackKind.FOLLOWING_REPLIES

    delay = delay_of_notifications[kind]

    notifications = [
        Notification(recipient=email_address, post=post, kind=kind, delay=delay)
        for email_address in post.topic.mails_to_notify()
    ]
    Notification.objects.bulk_create(notifications)
