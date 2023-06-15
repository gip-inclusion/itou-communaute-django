from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ForumSearchAppConfig(AppConfig):
    label = "forum_search"
    name = "lacommunaute.forum_search"
    verbose_name = _("Searches")
