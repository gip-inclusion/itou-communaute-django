import uuid

from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import urlencode

from lacommunaute.notification.models import Notification


class NotificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "notif" not in request.GET:
            return

        query_params = request.GET.copy()
        notif_uuid = query_params.pop("notif")[0]

        try:
            uuid.UUID(notif_uuid, version=4)
        except ValueError:
            pass
        else:
            Notification.objects.filter(uuid=notif_uuid).update(visited_at=timezone.now())

        new_url = (
            f"{request.path}?{urlencode({k: v for k, v in query_params.items() if v})}"
            if query_params
            else request.path
        )

        return HttpResponseRedirect(new_url)
