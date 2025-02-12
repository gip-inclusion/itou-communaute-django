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
            try:
                notification = Notification.objects.get(uuid=notif_uuid)
            except Notification.DoesNotExist:
                pass
            else:
                notification.visited_at = timezone.now()
                notification.save()
                EmailLastSeen.objects.seen(email=notification.recipient, kind=EmailLastSeenKind.VISITED)
        except ValueError:
            pass
