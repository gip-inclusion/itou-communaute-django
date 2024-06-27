from django.contrib import admin

from lacommunaute.edito.models import Edito


@admin.register(Edito)
class EditoAdmin(admin.ModelAdmin):
    list_display = ("title", "updated", "poster")
    raw_id_fields = ("poster",)
