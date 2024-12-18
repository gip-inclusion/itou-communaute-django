from django.contrib import admin
from machina.apps.forum_conversation.admin import PostAdmin as BasePostAdmin, TopicAdmin as BaseTopicAdmin

from lacommunaute.forum_conversation.models import CertifiedPost, Post, Topic


class PostAdmin(BasePostAdmin):
    def get_actions(self, request):
        # delete_selected action does not call delete method of the model
        # related topic is not update (last_post, posts_count) making
        # the website inconsistent
        return []


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
    list_filter = BaseTopicAdmin.list_filter + ("type",)


class CertifiedPostAdmin(admin.ModelAdmin):
    list_display = ("topic", "post", "user")
    raw_id_fields = (
        "topic",
        "post",
        "user",
    )


admin.site.unregister(Post)
admin.site.register(Post, PostAdmin)
admin.site.unregister(Topic)
admin.site.register(Topic, TopicAdmin)
admin.site.register(CertifiedPost, CertifiedPostAdmin)
