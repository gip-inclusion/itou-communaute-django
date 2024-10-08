from django.contrib import admin
from machina.apps.forum.admin import ForumAdmin as BaseForumAdmin

from lacommunaute.forum.models import ForumRating


class ForumAdmin(BaseForumAdmin):
    fieldsets = BaseForumAdmin.fieldsets
    fieldsets[0][1]["fields"] += ("short_description", "certified", "tags", "partner")


@admin.register(ForumRating)
class ForumRatingAdmin(admin.ModelAdmin):
    list_display = ("forum", "rating", "created")
    list_filter = ("forum",)
    list_display_links = ("rating",)
    raw_id_fields = ("forum", "user")
