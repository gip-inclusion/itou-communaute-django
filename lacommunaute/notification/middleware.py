import uuid

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from lacommunaute.notification.models import Notification


class NotificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "notif" not in request.GET:
            return

        notif_uuid = request.GET.get("notif", "")

        try:
            uuid.UUID(notif_uuid, version=4)
        except ValueError:
            pass
        else:
            Notification.objects.filter(uuid=notif_uuid).update(visited_at=timezone.now())
