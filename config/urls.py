from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from machina.core.loading import get_class

from lacommunaute.www.forum_conversation_views import urls as forum_conversation_extension_urls
from lacommunaute.www.forum_conversation_views.forum_polls import urls as forum_polls_extension_urls
from lacommunaute.www.forum_member_views import urls as forum_member_urls
from lacommunaute.www.forum_upvote_views import urls as forum_upvote_urls
from lacommunaute.www.forum_views import urls as forum_extension_urls
from lacommunaute.www.inclusion_connect_views import urls as inclusion_connect_urls


conversation_urlpatterns_factory = get_class("forum_conversation.urls", "urlpatterns_factory")
moderation_urlpatterns_factory = get_class("forum_moderation.urls", "urlpatterns_factory")
tracking_urlpatterns_factory = get_class("forum_tracking.urls", "urlpatterns_factory")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Inclusion Connect URLs.
    path("inclusion_connect/", include(inclusion_connect_urls)),
    # www.
    path("", include("lacommunaute.www.pages.urls")),
    path("", include("django.contrib.auth.urls")),
    path("members/", include(forum_member_urls)),
    path("", include(forum_conversation_extension_urls)),
    path("", include(forum_extension_urls)),
    path("", include(forum_polls_extension_urls)),
    path("", include(forum_upvote_urls)),
    # machina legacy
    path("", include(conversation_urlpatterns_factory.urlpatterns)),
    path("moderation/", include(moderation_urlpatterns_factory.urlpatterns)),
    path("tracking/", include(tracking_urlpatterns_factory.urlpatterns)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
