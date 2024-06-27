from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.models import Notification


# registered in apps.py
def create_post_notifications(sender, instance, **kwargs):
    """
    When a Post is created, we schedule notifications to users active in the thread
    """
    # NOTE: notifications solution depends on the fact that approval is completed at the time of creation
    if not instance.approved:
        return

    delay = NotificationDelay.ASAP if instance.is_first_reply else NotificationDelay.DAY
    kind = EmailSentTrackKind.FIRST_REPLY if instance.is_first_reply else EmailSentTrackKind.FOLLOWING_REPLIES

    notifications = [
        Notification(recipient=email_address, post=instance, kind=kind, delay=delay)
        for email_address in instance.topic.mails_to_notify()
    ]
    Notification.objects.bulk_create(notifications)
