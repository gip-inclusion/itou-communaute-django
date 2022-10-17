from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

from lacommunaute.www.forum_member import urls as forum_member_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    # www.
    path("", include("lacommunaute.www.pages.urls")),
    path("", include("lacommunaute.www.users.urls")),
    path("members/", include(forum_member_urls)),
    # machina legacy
    path("forum/", include(machina_urls)),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
