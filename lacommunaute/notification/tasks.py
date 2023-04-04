from django.conf import settings

from lacommunaute.notification.emails import bulk_send_user_to_list, send_email
from lacommunaute.notification.utils import collect_first_replies, collect_new_users_for_onboarding


def send_notifs_when_first_reply():

    first_replies = collect_first_replies()

    for url, subject, to, display_name in first_replies:
        params = {
            "url": f"{url}?mtm_campaign=firstreply&mtm_medium=email",
            "topic_subject": subject,
            "display_name": display_name,
        }
        send_email(to, params, settings.SIB_FIRST_REPLY_TEMPLATE)


def add_user_to_list_when_register():
    bulk_send_user_to_list(collect_new_users_for_onboarding(), settings.SIB_ONBOARDING_LIST)
