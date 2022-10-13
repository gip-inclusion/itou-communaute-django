from django.urls import path

from lacommunaute.www.forum_member.views import ForumProfileListView


app_name = "members"

urlpatterns = [
    path("", ForumProfileListView.as_view(), name="profiles"),
]
