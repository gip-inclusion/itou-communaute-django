import logging

import httpx
from django.conf import settings

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack


logger = logging.getLogger(__name__)


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


def collect_users_from_list(list_id: int) -> list | None:
    headers = {"api-key": settings.SIB_API_KEY, "Content-Type": "application/json", "Accept": "application/json"}
    response = httpx.get(f"{settings.SIB_CONTACT_LIST_URL}/{list_id}/contacts", headers=headers)
    if response.status_code == 200:
        return [
            {"email": contact["email"], "name": f'{contact["attributes"]["PRENOM"]} {contact["attributes"]["NOM"]}'}
            for contact in response.json()["contacts"]
            if not contact["emailBlacklisted"]
        ]
    return None
