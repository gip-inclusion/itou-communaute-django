from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import urlencode


class ProConnectLoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        query_params = request.GET.copy()

        if "proconnect_login" not in query_params:
            return

        query_params.pop("proconnect_login")
        new_url = (
            f"{request.path}?{urlencode({k: v for k, v in query_params.items() if v})}"
            if query_params
            else request.path
        )

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("openid_connect:authorize") + f"?next={new_url}")

        return HttpResponseRedirect(new_url)
