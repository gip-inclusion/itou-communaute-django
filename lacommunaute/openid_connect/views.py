import dataclasses
import logging

import httpx
import jwt
from django.contrib import messages
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import crypto
from django.utils.http import urlencode

from lacommunaute.openid_connect import constants
from lacommunaute.openid_connect.models import OIDConnectUserData, OpenID_State


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class OpenID_Session:
    token: str = None
    state: str = None
    previous_url: str = None
    next_url: str = None
    user_email: str = None
    request: str = None
    key: str = constants.OPENID_CONNECT_SESSION_KEY
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


def pro_connect_authorize(request):
    # Start a new session.
    previous_url = request.GET.get("previous_url", reverse("pages:home"))
    next_url = request.GET.get("next")
    sign_in = bool(request.GET.get("sign_in", False))

    proc_session = OpenID_Session(previous_url=previous_url, next_url=next_url)
    request = proc_session.bind_to_request(request)
    proc_session = request.session[constants.OPENID_CONNECT_SESSION_KEY]

    redirect_uri = request.build_absolute_uri(reverse("openid_connect:callback"))
    signed_csrf = OpenID_State.create_signed_csrf_token()
    data = {
        "response_type": "code",
        "client_id": constants.OPENID_CONNECT_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": constants.OPENID_CONNECT_SCOPES,
        "state": signed_csrf,
        "nonce": crypto.get_random_string(length=12),
        "acr_values": "eidas1",  # Force the eIDAS authentication.
    }
    redirect_url = (
        constants.OPENID_CONNECT_ENDPOINT_AUTHORIZE if not sign_in else constants.OPENID_CONNECT_ENDPOINT_REGISTRATIONS
    )
    return HttpResponseRedirect(f"{redirect_url}?{urlencode(data)}")


def pro_connect_callback(request):  # pylint: disable=too-many-return-statements
    code = request.GET.get("code")
    state = request.GET.get("state")
    if code is None or not OpenID_State.is_valid(state):
        return _redirect_to_login_page_on_error(error_msg="Missing code or invalid state.", request=request)

    proc_session = request.session[constants.OPENID_CONNECT_SESSION_KEY]
    token_redirect_uri = request.build_absolute_uri(reverse("openid_connect:callback"))

    data = {
        "client_id": constants.OPENID_CONNECT_CLIENT_ID,
        "client_secret": constants.OPENID_CONNECT_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": token_redirect_uri,
    }

    response = httpx.post(
        constants.OPENID_CONNECT_ENDPOINT_TOKEN,
        data=data,
        timeout=constants.OPENID_CONNECT_TIMEOUT,
    )

    if response.status_code != 200:
        return _redirect_to_login_page_on_error(error_msg="Impossible to get OpenID_ token.", request=request)

    # Contains access_token, token_type, expires_in, id_token
    token_data = response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return _redirect_to_login_page_on_error(error_msg="Access token field missing.", request=request)

    # Keep token_data["id_token"] to logout from IC.
    # At this step, we can update the user's fields in DB and create a session if required.
    proc_session["token"] = token_data["id_token"]
    proc_session["state"] = state
    request.session.modified = True

    # A token has been provided so it's time to fetch associated user infos
    # because the token is only valid for 5 seconds.
    response = httpx.get(
        constants.OPENID_CONNECT_ENDPOINT_USERINFO,
        params={"schema": "openid"},
        headers={"Authorization": "Bearer " + access_token},
        timeout=constants.OPENID_CONNECT_TIMEOUT,
    )
    if response.status_code != 200:
        return _redirect_to_login_page_on_error(error_msg="Impossible to get user infos.", request=request)

    user_data = jwt.decode(
        response.content,
        key=constants.OPENID_CONNECT_CLIENT_SECRET,
        algorithms=["HS256"],
        audience=constants.OPENID_CONNECT_CLIENT_ID,
    )

    if "sub" not in user_data:
        # 'sub' is the unique identifier from Inclusion Connect, we need that to match a user later on.
        return _redirect_to_login_page_on_error(error_msg="Sub parameter missing.", request=request)

    proc_user_data = OIDConnectUserData.from_user_info(user_data)
    user, _ = proc_user_data.create_or_update_user()

    if not user.is_active:
        logout_url_params = {
            "redirect_url": proc_session["previous_url"],
        }
        next_url = f"{reverse('openid_connect:logout')}?{urlencode(logout_url_params)}"
        return HttpResponseRedirect(next_url)

    login(request, user)

    next_url = proc_session["next_url"] or reverse("pages:home")
    return HttpResponseRedirect(next_url)


def pro_connect_logout(request):
    token = request.GET.get("token")
    post_logout_redirect_uri = request.GET.get("redirect_url", reverse("pages:home"))

    # Fallback on session data.
    if not token:
        proc_session = request.session.get(constants.OPENID_CONNECT_SESSION_KEY)
        if not proc_session:
            raise KeyError("Missing session key.")
        token = proc_session["token"]

    params = {
        "id_token_hint": token,
        "post_logout_redirect_uri": request.build_absolute_uri(post_logout_redirect_uri),
    }
    complete_url = f"{constants.OPENID_CONNECT_ENDPOINT_LOGOUT}?{urlencode(params)}"

    logout(request)

    return HttpResponseRedirect(complete_url)
