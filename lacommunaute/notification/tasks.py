from lacommunaute.forum_conversation.utils import collect_first_replies
from lacommunaute.notification.emails import send_email


def send_notifs_when_first_reply():
    templateId = 2

    first_replies = collect_first_replies()

    for url, subject, to, display_name in first_replies:
        params = {
            "url": url,
            "topic_subject": subject,
            "display_name": display_name,
        }
        send_email(to, params, templateId)
