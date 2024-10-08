from django.conf import settings
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone

from config.settings.base import DEFAULT_FROM_EMAIL, NEW_MESSAGES_EMAIL_MAX_PREVIEW, SIB_NEW_MESSAGES_TEMPLATE
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.notification.emails import bulk_send_user_to_list, collect_users_from_list, send_email
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.models import Notification
from lacommunaute.notification.utils import collect_new_users_for_onboarding, get_serialized_messages


def send_messages_notifications(delay: NotificationDelay):
    """Notifications are scheduled in the application and then processed later by this task"""

    notifications = Notification.objects.filter(delay=delay, sent_at__isnull=True, post__isnull=False).select_related(
        "post", "post__topic", "post__poster"
    )

    def get_grouped_notifications():
        return notifications.group_by_recipient()

    grouped_notifications = get_grouped_notifications()
    for recipient in grouped_notifications.keys():
        recipient_notifications = grouped_notifications[recipient]
        message_count = len(recipient_notifications)
        message_count_text = f"{message_count} message{pluralize(message_count, 's')}"

        params = {
            "email_object": "Bonne nouvelle, ça bouge pour vous dans la communauté !",
            "email_thumbnail": (f"Vous avez {message_count_text} à découvrir sur la communauté de l'inclusion"),
            "messages": get_serialized_messages(recipient_notifications[:NEW_MESSAGES_EMAIL_MAX_PREVIEW]),
        }
        send_email(
            to=[{"email": DEFAULT_FROM_EMAIL}],
            params=params,
            bcc=[{"email": recipient}],
            kind=EmailSentTrackKind.FOLLOWING_REPLIES,
            template_id=SIB_NEW_MESSAGES_TEMPLATE,
        )

    notifications.update(sent_at=timezone.now())


def add_user_to_list_when_register():
    new_users = collect_new_users_for_onboarding()
    if new_users:
        bulk_send_user_to_list(new_users, settings.SIB_ONBOARDING_LIST)


def send_notifs_on_unanswered_topics(list_id: int) -> None:
    contacts = collect_users_from_list(list_id)

    if contacts:
        count = Topic.objects.unanswered().count()
        link = (
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}",
            reverse("forum_conversation_extension:topics"),
            "?filter=NEW&mtm_campaign=unsanswered&mtm_medium=email#community",
        )

        params = {"count": count, "link": "".join(link)}

        if count > 0:
            send_email(
                to=contacts,
                params=params,
                template_id=settings.SIB_UNANSWERED_QUESTION_TEMPLATE,
                kind=EmailSentTrackKind.PENDING_TOPIC,
            )
