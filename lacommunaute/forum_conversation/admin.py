from django.contrib import admin
from machina.apps.forum_conversation.admin import TopicAdmin as BaseTopicAdmin

from lacommunaute.forum_conversation.models import CertifiedPost


class TopicAdmin(BaseTopicAdmin):
    raw_id_fields = (
        "poster",
        "subscribers",
    )


class CertifiedPostAdmin(admin.ModelAdmin):
    list_display = ("topic", "post", "user")
    raw_id_fields = (
        "topic",
        "post",
        "user",
    )


admin.site.register(CertifiedPost, CertifiedPostAdmin)
