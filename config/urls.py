from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from machina import urls as machina_urls

from lacommunaute.www.forum_conversation import urls as forum_conversation_extension_urls
from lacommunaute.www.forum_member import urls as forum_member_urls


urlpatterns = [
    path("admin/", admin.site.urls),
    # Inclusion Connect URLs.
    path(
        "inclusion_connect/",
        include("lacommunaute.www.inclusion_connect.urls"),
    ),
    # www.
    path("", include("lacommunaute.www.pages.urls")),
    path("", include("django.contrib.auth.urls")),
    path("members/", include(forum_member_urls)),
    path("forum/", include(forum_conversation_extension_urls)),
    # machina legacy
    path("forum/", include(machina_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
