import dataclasses
import json
import logging

import httpx
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import crypto
from django.utils.http import urlencode

from lacommunaute.inclusion_connect import constants
from lacommunaute.inclusion_connect.models import InclusionConnectState, OIDConnectUserData
from lacommunaute.utils.urls import get_absolute_url


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class InclusionConnectSession:
    token: str = None
    state: str = None
    previous_url: str = None
    next_url: str = None
    user_email: str = None
    request: str = None
    key: str = constants.INCLUSION_CONNECT_SESSION_KEY
    channel: str = None
    # Tells us where did the user came from so that we can adapt
    # error messages in the callback view.

    def asdict(self):
        return dataclasses.asdict(self)

    def bind_to_request(self, request):
        request.session[self.key] = dataclasses.asdict(self)
        request.session.has_changed = True
        return request


def _redirect_to_login_page_on_error(error_msg, request=None):
    if request:
        messages.error(request, "Une erreur technique est survenue. Merci de recommencer.")
    logger.error(error_msg)
    return HttpResponseRedirect(reverse("pages:home"))


def inclusion_connect_authorize(request):
    # Start a new session.
    previous_url = request.GET.get("previous_url", reverse("pages:home"))
    next_url = request.GET.get("next_url")
    sign_in = bool(request.GET.get("sign_in", False))

    ic_session = InclusionConnectSession(previous_url=previous_url, next_url=next_url)
    request = ic_session.bind_to_request(request)
    ic_session = request.session[constants.INCLUSION_CONNECT_SESSION_KEY]

    redirect_uri = get_absolute_url(reverse("inclusion_connect:callback"))
    signed_csrf = InclusionConnectState.create_signed_csrf_token()
    data = {
        "response_type": "code",
        "client_id": constants.INCLUSION_CONNECT_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": constants.INCLUSION_CONNECT_SCOPES,
        "state": signed_csrf,
        "nonce": crypto.get_random_string(length=12),
        "from": "communaute",  # Display a "La communauté" logo on the connection page.
    }
    redirect_url = (
        constants.INCLUSION_CONNECT_ENDPOINT_AUTHORIZE
        if not sign_in
        else constants.INCLUSION_CONNECT_ENDPOINT_REGISTRATIONS
    )
    return HttpResponseRedirect(f"{redirect_url}?{urlencode(data)}")


def inclusion_connect_callback(request):  # pylint: disable=too-many-return-statements
    code = request.GET.get("code")
    state = request.GET.get("state")
    if code is None or not InclusionConnectState.is_valid(state):
        return _redirect_to_login_page_on_error(error_msg="Missing code or invalid state.", request=request)

    ic_session = request.session[constants.INCLUSION_CONNECT_SESSION_KEY]
    token_redirect_uri = get_absolute_url(reverse("inclusion_connect:callback"))

    data = {
        "client_id": constants.INCLUSION_CONNECT_CLIENT_ID,
        "client_secret": constants.INCLUSION_CONNECT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": token_redirect_uri,
    }

    response = httpx.post(
        constants.INCLUSION_CONNECT_ENDPOINT_TOKEN,
        data=data,
        timeout=constants.INCLUSION_CONNECT_TIMEOUT,
    )

    if response.status_code != 200:
        return _redirect_to_login_page_on_error(error_msg="Impossible to get IC token.", request=request)

    # Contains access_token, token_type, expires_in, id_token
    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return _redirect_to_login_page_on_error(error_msg="Access token field missing.", request=request)

    # Keep token_data["id_token"] to logout from IC.
    # At this step, we can update the user's fields in DB and create a session if required.
    ic_session["token"] = token_data["id_token"]
    ic_session["state"] = state
    request.session.modified = True

    # A token has been provided so it's time to fetch associated user infos
    # because the token is only valid for 5 seconds.
    response = httpx.get(
        constants.INCLUSION_CONNECT_ENDPOINT_USERINFO,
        params={"schema": "openid"},
        headers={"Authorization": "Bearer " + access_token},
        timeout=constants.INCLUSION_CONNECT_TIMEOUT,
    )
    if response.status_code != 200:
        return _redirect_to_login_page_on_error(error_msg="Impossible to get user infos.", request=request)

    try:
        user_data = json.loads(response.content.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        return _redirect_to_login_page_on_error(error_msg="Impossible to decode user infos.", request=request)

    if "sub" not in user_data:
        # 'sub' is the unique identifier from Inclusion Connect, we need that to match a user later on.
        return _redirect_to_login_page_on_error(error_msg="Sub parameter missing.", request=request)

    ic_user_data = OIDConnectUserData.from_user_info(user_data)
    user, _ = ic_user_data.create_or_update_user()

    if not user.is_active:
        logout_url_params = {
            "redirect_url": ic_session["previous_url"],
        }
        next_url = f"{reverse('inclusion_connect:logout')}?{urlencode(logout_url_params)}"
        return HttpResponseRedirect(next_url)

    login(request, user)
    next_url = ic_session["next_url"] or reverse("pages:home")
    return HttpResponseRedirect(next_url)


def inclusion_connect_logout(request):
    token = request.GET.get("token")
    state = request.GET.get("state")
    post_logout_redirect_url = request.GET.get("redirect_url", reverse("pages:home"))

    # Fallback on session data.
    if not token:
        ic_session = request.session.get(constants.INCLUSION_CONNECT_SESSION_KEY)
        if not ic_session:
            raise KeyError("Missing session key.")
        token = ic_session["token"]
        state = ic_session["state"]

    params = {
        "id_token_hint": token,
        "state": state,
    }
    complete_url = f"{constants.INCLUSION_CONNECT_ENDPOINT_LOGOUT}?{urlencode(params)}"
    # Logout user from IC with HTTPX to benefit from respx in tests
    # and to handle post logout redirection more easily.
    response = httpx.get(complete_url)
    if response.status_code != 200:
        logger.error("Error during IC logout. Status code: %s", response.status_code)

    # Logout user from Django
    logout(request)

    return HttpResponseRedirect(post_logout_redirect_url)
