from django.urls import path

from lacommunaute.www.event_views.views import (
    EventCreateView,
    EventDeleteView,
    EventListView,
    EventUpdateView,
    calendar,
    calendar_data,
)


app_name = "event"


urlpatterns = [
    path("", calendar, name="calendar"),
    path("create/", EventCreateView.as_view(), name="create"),
    path("<int:pk>/update/", EventUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", EventDeleteView.as_view(), name="delete"),
    path("myevents/", EventListView.as_view(), name="myevents"),
    path("events/events.json", calendar_data, name="data_source"),
]
