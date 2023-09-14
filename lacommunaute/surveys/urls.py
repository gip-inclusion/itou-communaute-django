from django.urls import path

from lacommunaute.surveys import views


app_name = "surveys"

urlpatterns = [
    path("dsp/create/", views.DSPCreateView.as_view(), name="dsp_create"),
    path("dsp/<int:pk>/", views.DSPDetailView.as_view(), name="dsp_detail"),
]
