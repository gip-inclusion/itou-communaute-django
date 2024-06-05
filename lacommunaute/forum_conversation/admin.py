from django.contrib import admin
from machina.apps.forum_conversation.admin import TopicAdmin as BaseTopicAdmin

from lacommunaute.forum_conversation.models import CertifiedPost, Post, Topic


class PostInline(admin.StackedInline):
    model = Post
    list_display = ("__str__", "poster", "updated", "approved")
    raw_id_fields = (
        "poster",
        "topic",
    )
    extra = 0


class TopicAdmin(BaseTopicAdmin):
    raw_id_fields = (
        "poster",
        "subscribers",
    )
    inlines = [
        PostInline,
    ]


class CertifiedPostAdmin(admin.ModelAdmin):
    list_display = ("topic", "post", "user")
    raw_id_fields = (
        "topic",
        "post",
        "user",
    )


admin.site.unregister(Topic)
admin.site.register(Topic, TopicAdmin)
admin.site.register(CertifiedPost, CertifiedPostAdmin)
