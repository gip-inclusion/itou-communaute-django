from django.contrib import admin
from machina.apps.forum_conversation.admin import TopicAdmin as BaseTopicAdmin

from lacommunaute.forum_conversation.models import CertifiedPost


# TODO vincentporte, need to be fixed, likers field does not appear like a raw id fields
class TopicAdmin(BaseTopicAdmin):
    raw_id_fields = (
        "poster",
        "subscribers",
        "likers",
    )


class CertifiedPostAdmin(admin.ModelAdmin):
    list_display = ("topic", "post", "user")
    raw_id_fields = (
        "topic",
        "post",
        "user",
    )


admin.site.register(CertifiedPost, CertifiedPostAdmin)
