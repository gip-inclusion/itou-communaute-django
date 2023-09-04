from django.contrib import admin
from django.utils.html import format_html

from lacommunaute.forum_file.models import PublicFile


@admin.register(PublicFile)
class PublicFileAdmin(admin.ModelAdmin):
    list_display = ("user", "created", "file_url", "keywords")
    list_filter = ("created",)
    raw_id_fields = ("user",)
    search_fields = ("user__email", "keywords", "file__name")
    fields = ("file", "keywords")

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        obj.save()

    def file_url(self, obj):
        return format_html(f'<a href="{obj.get_file_url()}" target="_blank">{obj.get_file_url()}</a>')

    file_url.short_description = "URL du fichier"
