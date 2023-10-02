from django.urls import path

from lacommunaute.event.views import (
    EventCreateView,
    EventDeleteView,
    EventDetailView,
    EventListView,
    EventMonthArchiveView,
    EventUpdateView,
)


app_name = "event"


urlpatterns = [
    path("create/", EventCreateView.as_view(), name="create"),
    path("<int:pk>/", EventDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", EventUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", EventDeleteView.as_view(), name="delete"),
    path("myevents/", EventListView.as_view(), name="myevents"),
    path("events/<int:year>/<int:month>/", EventMonthArchiveView.as_view(), name="month"),
    path("events/", EventMonthArchiveView.as_view(), name="current"),
]
