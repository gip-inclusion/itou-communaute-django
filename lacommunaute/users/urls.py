from django.urls import path

from lacommunaute.users.views import (
    CreateUserView,
    LoginView,
    login_with_link,
    logout_view,
)


app_name = "users"

urlpatterns = [
    path("create/", CreateUserView.as_view(), name="create"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/<str:uidb64>/<str:token>/", login_with_link, name="login_with_link"),
    path("logout/", logout_view, name="logout"),
]
