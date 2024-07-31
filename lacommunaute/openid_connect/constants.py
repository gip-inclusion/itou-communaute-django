import datetime

from django.conf import settings


OPENID_CONNECT_SCOPES = "openid email given_name usual_name"

OPENID_CONNECT_CLIENT_ID = settings.OPENID_CONNECT_CLIENT_ID
OPENID_CONNECT_CLIENT_SECRET = settings.OPENID_CONNECT_CLIENT_SECRET

OPENID_CONNECT_ENDPOINT = "{base_url}".format(
    base_url=settings.OPENID_CONNECT_BASE_URL,
)
OPENID_CONNECT_ENDPOINT_AUTHORIZE = f"{OPENID_CONNECT_ENDPOINT}/authorize"
OPENID_CONNECT_ENDPOINT_REGISTRATIONS = f"{OPENID_CONNECT_ENDPOINT}/register"
OPENID_CONNECT_ENDPOINT_TOKEN = f"{OPENID_CONNECT_ENDPOINT}/token"
OPENID_CONNECT_ENDPOINT_USERINFO = f"{OPENID_CONNECT_ENDPOINT}/userinfo"
OPENID_CONNECT_ENDPOINT_LOGOUT = f"{OPENID_CONNECT_ENDPOINT}/session/end"

# These expiration times have been chosen arbitrarily.
OPENID_CONNECT_TIMEOUT = 60

OPENID_CONNECT_SESSION_KEY = "pro_connect"

# This expiration time has been chosen arbitrarily.
OIDC_STATE_EXPIRATION = datetime.timedelta(hours=1)
