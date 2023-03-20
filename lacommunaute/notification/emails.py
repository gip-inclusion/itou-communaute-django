import logging

import httpx

from config.settings.base import DEFAULT_FROM_EMAIL, SIB_API_KEY, SIB_CONTACTS_URL, SIB_SMTP_URL
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack


logger = logging.getLogger(__name__)


def send_email(to, params, template_id):
    headers = {"api-key": SIB_API_KEY, "Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "sender": {"name": "La Communauté", "email": DEFAULT_FROM_EMAIL},
        "to": [{"email": to}],
        "params": params,
        "templateId": template_id,
    }

    response = httpx.post(SIB_SMTP_URL, headers=headers, json=payload)

    EmailSentTrack.objects.create(
        status_code=response.status_code, response=response.text, datas=payload, kind=EmailSentTrackKind.FIRST_REPLY
    )


def add_user_to_list(email, firstname, lastname, list_id):
    payload = {
        "email": email,
        "attributes": {
            "FNAME": firstname,
            "LNAME": lastname,
        },
        "emailBlacklisted": False,
        "smsBlacklisted": False,
        "listIds": [list_id],
        "updateEnabled": True,
    }
    headers = {"accept": "application/json", "content-type": "application/json", "api-key": SIB_API_KEY}
    response = httpx.post(SIB_CONTACTS_URL, headers=headers, json=payload)

    EmailSentTrack.objects.create(
        status_code=response.status_code, response=response.text, datas=payload, kind=EmailSentTrackKind.ONBOARDING
    )
