from django.contrib import admin

from lacommunaute.forum.models import Forum
from lacommunaute.partner.models import Partner


class ForumInline(admin.TabularInline):
    model = Forum
    extra = 0
    fields = ("name", "short_description")
    readonly_fields = ("name", "short_description")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created")
    search_fields = ("name",)
    list_filter = ("created",)
    inlines = [ForumInline]
