from django.contrib import admin

from lacommunaute.partner.models import Partner


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "created")
    search_fields = ("name",)
    list_filter = ("created",)
