from django.urls import path

from lacommunaute.openid_connect import views


app_name = "openid_connect"

urlpatterns = [
    path("authorize", views.openid_connect_authorize, name="authorize"),
    path("callback", views.openid_connect_callback, name="callback"),
    path("logout", views.openid_connect_logout, name="logout"),
]
