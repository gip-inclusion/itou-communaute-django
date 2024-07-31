from django.urls import path

from lacommunaute.openid_connect import views


app_name = "openid_connect"

urlpatterns = [
    path("authorize", views.pro_connect_authorize, name="authorize"),
    path("callback", views.pro_connect_callback, name="callback"),
    path("logout", views.pro_connect_logout, name="logout"),
]
