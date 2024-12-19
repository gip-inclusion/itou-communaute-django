import logging
from urllib.parse import urljoin

import httpx
from django.conf import settings

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack


logger = logging.getLogger(__name__)

SIB_SMTP_URL = urljoin(settings.SIB_URL, settings.SIB_SMTP_ROUTE)
SIB_CONTACTS_URL = urljoin(settings.SIB_URL, settings.SIB_CONTACTS_ROUTE)


def send_email(to, params, template_id, kind, bcc=None):
    headers = {"api-key": settings.SIB_API_KEY, "Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "sender": {"name": "La Communauté", "email": settings.DEFAULT_FROM_EMAIL},
        "to": to,
        "params": params,
        "templateId": template_id,
    }
    if bcc:
        payload["bcc"] = bcc

    if settings.DEBUG:
        # We don't want to send emails in debug mode, payload is saved in the database
        response = httpx.Response(200, json={"message": "OK"})
    else:
        response = httpx.post(SIB_SMTP_URL, headers=headers, json=payload)

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
    response = httpx.post(SIB_CONTACTS_URL, headers=headers, json=payload)

    EmailSentTrack.objects.create(
        status_code=response.status_code, response=response.text, datas=payload, kind=EmailSentTrackKind.ONBOARDING
    )
