from django.contrib import admin

from lacommunaute.forum_stats.models import SearchCollectionPeriod, SearchQuery, Stat


class StatAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "value", "period")
    list_filter = ("name", "date", "period")


class SearchCollectionPeriodAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")


class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("period", "nb_visits")


admin.site.register(Stat, StatAdmin)
admin.site.register(SearchCollectionPeriod, SearchCollectionPeriodAdmin)
admin.site.register(SearchQuery, SearchQueryAdmin)
