from django.urls import path

from lacommunaute.partner.views import PartnerDetailView, PartnerListView


app_name = "partner"


urlpatterns = [
    path("", PartnerListView.as_view(), name="list"),
    path("<str:slug>-<int:pk>/", PartnerDetailView.as_view(), name="detail"),
]
