from django.contrib import admin

from lacommunaute.metabase.models import ForumTable, PostTable


@admin.register(ForumTable)
class ForumTableAdmin(admin.ModelAdmin):
    readonly_fields = (
        "name",
        "kind",
        "type",
        "short_description_boolean",
        "description_boolean",
        "parent_name",
        "direct_topics_count",
        "upvotes_count",
        "last_post_at",
        "last_updated_at",
        "extracted_at",
    )

    def has_add_permission(self, request):
        return False


@admin.register(PostTable)
class PostTableAdmin(admin.ModelAdmin):
    readonly_fields = (
        "subject",
        "subject_likes_count",
        "forum_name",
        "poster",
        "is_anonymous_post",
        "certifier",
        "post_upvotes_count",
        "attachments_count",
        "tags_list",
        "approved_boolean",
        "topic_created_at",
        "post_created_at",
        "post_position_in_topic",
        "updates_count",
        "post_last_updated_at",
        "extracted_at",
    )

    def has_add_permission(self, request):
        return False
