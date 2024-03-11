from django.contrib import admin

from lacommunaute.surveys.models import DSP, Recommendation


@admin.register(DSP)
class DSPAdmin(admin.ModelAdmin):
    list_display = ("user", "created")
    raw_id_fields = ("user",)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("category", "text", "dora_cats", "dora_subs")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
