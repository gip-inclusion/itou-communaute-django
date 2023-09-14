from django.contrib import admin

from lacommunaute.surveys.models import DSP


@admin.register(DSP)
class DSPAdmin(admin.ModelAdmin):
    list_display = ("user", "created")
    raw_id_fields = ("user",)
