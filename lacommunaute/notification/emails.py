import logging

import httpx

from config.settings.base import DEFAULT_FROM_EMAIL, SIB_API_KEY, SIB_URL
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

    response = httpx.post(SIB_URL, headers=headers, json=payload)

    EmailSentTrack.objects.create(status_code=response.status_code, response=response.text, datas=payload)
