from django.conf import settings

from lacommunaute.notification.emails import bulk_send_user_to_list, send_email
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.utils import collect_first_replies, collect_new_users_for_onboarding


def send_notifs_when_first_reply():

    first_replies = collect_first_replies()

    for url, subject, to, display_name in first_replies:
        contacts = [{"email": to}]
        params = {
            "url": f"{url}?mtm_campaign=firstreply&mtm_medium=email",
            "topic_subject": subject,
            "display_name": display_name,
        }
        send_email(
            to=contacts,
            params=params,
            template_id=settings.SIB_FIRST_REPLY_TEMPLATE,
            kind=EmailSentTrackKind.FIRST_REPLY,
        )


def add_user_to_list_when_register():
    bulk_send_user_to_list(collect_new_users_for_onboarding(), settings.SIB_ONBOARDING_LIST)
