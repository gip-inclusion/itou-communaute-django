from lacommunaute.notification.enums import EmailSentTrackKind, delay_of_notifications
from lacommunaute.notification.models import Notification


# registered in apps.py
def create_post_notifications(sender, instance, **kwargs):
    """
    When a Post is created, we schedule notifications to users active in the thread
    """
    # NOTE: notifications solution depends on the fact that approval is completed at the time of creation
    if not instance.approved:
        return

    if instance.is_topic_head:
        kind = EmailSentTrackKind.PENDING_TOPIC
    elif instance.is_first_reply:
        kind = EmailSentTrackKind.FIRST_REPLY
    else:
        kind = EmailSentTrackKind.FOLLOWING_REPLIES

    delay = delay_of_notifications[kind]

    notifications = [
        Notification(recipient=email_address, post=instance, kind=kind, delay=delay)
        for email_address in instance.topic.mails_to_notify()
    ]
    Notification.objects.bulk_create(notifications)
