from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from machina import urls as machina_urls

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
    # machina legacy
    path("forum/", include(machina_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

# error pages
handler400 = TemplateView.as_view(template_name="pages/400.html")
handler403 = TemplateView.as_view(template_name="pages/403.html")
handler404 = TemplateView.as_view(template_name="pages/404.html")
handler500 = TemplateView.as_view(template_name="pages/500.html")
