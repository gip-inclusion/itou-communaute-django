from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path, re_path
from machina.core.loading import get_class

from lacommunaute.event import urls as event_urls
from lacommunaute.forum import urls as forum_extension_urls
from lacommunaute.forum_conversation import urls as forum_conversation_extension_urls
from lacommunaute.forum_conversation.forum_polls import urls as forum_polls_extension_urls
from lacommunaute.forum_member import urls as forum_member_urls
from lacommunaute.forum_moderation import urls as forum_moderation_urls
from lacommunaute.forum_upvote import urls as forum_upvote_urls
from lacommunaute.openid_connect import urls as openid_connect_urls
from lacommunaute.pages import urls as pages_urls
from lacommunaute.partner import urls as partner_urls
from lacommunaute.search import urls as search_urls
from lacommunaute.stats import urls as stats_urls
from lacommunaute.surveys import urls as surveys_urls


conversation_urlpatterns_factory = get_class("forum_conversation.urls", "urlpatterns_factory")
moderation_urlpatterns_factory = get_class("forum_moderation.urls", "urlpatterns_factory")
tracking_urlpatterns_factory = get_class("forum_tracking.urls", "urlpatterns_factory")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Pro Connect URLs.
    path("pro_connect/", include(openid_connect_urls)),
    # www.
    path("", include(pages_urls)),
    path("members/", include(forum_member_urls)),
    path("", include(forum_conversation_extension_urls)),
    path("", include(forum_extension_urls)),
    path("", include(forum_polls_extension_urls)),
    path("", include(forum_upvote_urls)),
    path("search/", include(search_urls)),
    path("", include(forum_moderation_urls)),
    path("calendar/", include(event_urls)),
    path("surveys/", include(surveys_urls)),
    path("partenaires/", include(partner_urls)),
    path("statistiques/", include(stats_urls)),
    # machina legacy
    path("", include(conversation_urlpatterns_factory.urlpatterns)),
    path("moderation/", include(moderation_urlpatterns_factory.urlpatterns)),
    path("tracking/", include(tracking_urlpatterns_factory.urlpatterns)),
]

if settings.DEBUG is True:
    urlpatterns += [path("", include("django.contrib.auth.urls"))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r"^(?P<url>.*/)$", views.flatpage),
]

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
