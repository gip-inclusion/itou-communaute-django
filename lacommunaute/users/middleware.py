from logging import getLogger

from django.utils.deprecation import MiddlewareMixin

from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.models import EmailLastSeen


logger = getLogger("lacommunaute")


class MarkAsSeenLoggedUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            EmailLastSeen.objects.seen(email=request.user.email, kind=EmailLastSeenKind.LOGGED)
