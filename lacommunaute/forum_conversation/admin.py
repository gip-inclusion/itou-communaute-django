from django.contrib import admin
from machina.models.fields import MarkupTextField, MarkupTextFieldWidget

from lacommunaute.forum_conversation.forum_attachments.models import Attachment
from lacommunaute.forum_conversation.models import Post, Topic


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


class PostAdmin(admin.ModelAdmin):
    """The Post model admin."""

    inlines = [
        AttachmentInline,
    ]
    list_display = ("__str__", "topic", "poster", "updated", "approved")
    list_filter = (
        "created",
        "updated",
    )
    raw_id_fields = (
        "poster",
        "topic",
    )
    search_fields = ("content",)
    list_editable = ("approved",)

    formfield_overrides = {
        MarkupTextField: {"widget": MarkupTextFieldWidget},
    }


class TopicAdmin(admin.ModelAdmin):
    """The Topic model admin."""

    list_display = ("subject", "forum", "created", "posts_count", "approved", "type")
    list_filter = ("created", "updated", "type")
    raw_id_fields = ("poster", "subscribers", "likers")
    search_fields = ("subject",)
    list_editable = ("approved",)


admin.site.register(Topic, TopicAdmin)
admin.site.register(Post, PostAdmin)
