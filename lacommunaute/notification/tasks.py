from config.settings.base import SIB_FIRST_REPLY_TEMPLATE
from lacommunaute.notification.emails import send_email
from lacommunaute.notification.utils import collect_first_replies


def send_notifs_when_first_reply():

    first_replies = collect_first_replies()

    for url, subject, to, display_name in first_replies:
        params = {
            "url": f"{url}?mtm_campaign=firstreply&mtm_medium=email",
            "topic_subject": subject,
            "display_name": display_name,
        }
        send_email(to, params, SIB_FIRST_REPLY_TEMPLATE)
