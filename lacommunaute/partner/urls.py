from django.urls import path

from lacommunaute.partner.views import PartnerCreateView, PartnerDetailView, PartnerListView, PartnerUpdateView


app_name = "partner"


urlpatterns = [
    path("", PartnerListView.as_view(), name="list"),
    path("<str:slug>-<int:pk>/", PartnerDetailView.as_view(), name="detail"),
    path("<str:slug>-<int:pk>/update/", PartnerUpdateView.as_view(), name="update"),
    path("create/", PartnerCreateView.as_view(), name="create"),
]
