import uuid

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from lacommunaute.notification.models import Notification
from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.models import EmailLastSeen


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
            notifs = Notification.objects.filter(uuid=notif_uuid)
            notifs.update(visited_at=timezone.now())
            [EmailLastSeen.objects.seen(email=notif.recipient, kind=EmailLastSeenKind.VISITED) for notif in notifs]
