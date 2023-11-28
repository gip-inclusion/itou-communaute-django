from django.contrib import admin

from lacommunaute.metabase.models import ForumTable


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
