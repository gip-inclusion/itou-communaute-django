import logging

import httpx
from django.conf import settings

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack


logger = logging.getLogger(__name__)


def send_email(to, params, template_id, kind):
    headers = {"api-key": settings.SIB_API_KEY, "Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "sender": {"name": "La Communauté", "email": settings.DEFAULT_FROM_EMAIL},
        "to": to,
        "params": params,
        "templateId": template_id,
    }

    response = httpx.post(settings.SIB_SMTP_URL, headers=headers, json=payload)

    EmailSentTrack.objects.create(
        status_code=response.status_code,
        response=response.text,
        datas=payload,
        kind=kind,
    )


def bulk_send_user_to_list(users, list_id):
    payload = {
        "jsonBody": [
            {"email": user.email, "attributes": {"NOM": user.last_name, "PRENOM": user.first_name}} for user in users
        ],
        "emailBlacklist": False,
        "smsBlacklist": False,
        "listIds": [list_id],
        "updateExistingContacts": True,
        "emptyContactsAttributes": True,
    }
    headers = {"accept": "application/json", "content-type": "application/json", "api-key": settings.SIB_API_KEY}
    response = httpx.post(settings.SIB_CONTACTS_URL, headers=headers, json=payload)

    EmailSentTrack.objects.create(
        status_code=response.status_code, response=response.text, datas=payload, kind=EmailSentTrackKind.ONBOARDING
    )
