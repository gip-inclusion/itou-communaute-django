import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.html import format_html
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import FormView

from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.notification.emails import send_email
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.users.enums import IdentityProvider
from lacommunaute.users.forms import CreateUserForm, LoginForm
from lacommunaute.users.models import User
from lacommunaute.utils.urls import clean_next_url


logger = logging.getLogger(__name__)


def send_magic_link(request, user, next_url):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    url = reverse("users:login_with_link", kwargs={"uidb64": uidb64, "token": token})
    query_params = urlencode({"next": clean_next_url(next_url)})
    login_link = f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{url}?{query_params}"

    send_email(
        to=[{"email": user.email}],
        params={"display_name": get_forum_member_display_name(user), "login_link": login_link},
        kind=EmailSentTrackKind.MAGIC_LINK,
        template_id=settings.SIB_MAGIC_LINK_TEMPLATE,
    )

    if settings.ENVIRONMENT == "DEV":
        message = format_html('<a href="{0}">{0}</a> sent to {1}', login_link, user.email)
        messages.success(request, message)


class LoginView(FormView):
    template_name = "registration/login_with_magic_link.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        # TODO vincentporte : add a control to check
        # if user uses a blocked email or a blocked domain
        if request.user.is_authenticated:
            next_url = request.GET.get("next", "/")
            return redirect(clean_next_url(next_url))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        next_url = self.request.POST.get("next", "/")
        email = form.cleaned_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            base_url = reverse("users:create")
            query_params = {"email": email, "next": clean_next_url(next_url)}
            return HttpResponseRedirect(f"{base_url}?{urlencode(query_params)}")

        send_magic_link(self.request, user, next_url)
        return render(self.request, "registration/login_link_sent.html", {"email": email})


class CreateUserView(FormView):
    template_name = "registration/create_user.html"
    form_class = CreateUserForm

    def get_initial(self):
        return super().get_initial() | {"email": self.request.GET.get("email", "")}

    def form_valid(self, form):
        next_url = self.request.POST.get("next", "/")
        email = form.cleaned_data["email"]
        first_name = form.cleaned_data["first_name"]
        last_name = form.cleaned_data["last_name"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                identity_provider=IdentityProvider.MAGIC_LINK,
            )
            ForumProfile.objects.create(user=user)

        send_magic_link(self.request, user, next_url)
        return render(self.request, "registration/login_link_sent.html", {"email": email})


def login_with_link(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        login(request, user)
        request.session[IdentityProvider.MAGIC_LINK.name] = 1
        next_url = clean_next_url(request.GET.get("next", "/"))
        return HttpResponseRedirect(next_url)

    return HttpResponseRedirect(reverse("users:login"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("pages:home"))
