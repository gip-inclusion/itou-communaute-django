from django.urls import path

from lacommunaute.openid_connect import views


app_name = "openid_connect"

urlpatterns = [
    path("pro_connect/authorize", views.pro_connect_authorize, name="authorize"),
    path("pro_connect/callback", views.pro_connect_callback, name="callback"),
    path("pro_connect/logout", views.pro_connect_logout, name="logout"),
]
