from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from lacommunaute.forum.models import Forum
from lacommunaute.stats.models import DocumentationStat, ForumStat, Stat


class ForumWithStatsFilter(admin.SimpleListFilter):
    title = "Forum"
    parameter_name = "forum"

    def lookups(self, request, model_admin):
        forums_with_stats = model_admin.model.objects.values_list("forum", flat=True)
        return Forum.objects.filter(pk__in=forums_with_stats).values_list("pk", "name")

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(forum=self.value())
        return queryset


class DocumentationContentTypeFilter(admin.SimpleListFilter):
    title = "Documentation type"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        content_types = ContentType.objects.filter(model__in=["category", "document"], app_label="documentation")

        return [(ct.id, ct.name) for ct in content_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        return queryset


class BaseStatAdmin(admin.ModelAdmin):
    list_display = ("explicit_period",)
    list_filter = ("date", "period")

    @admin.display(ordering="date")
    def explicit_period(self, obj):
        if obj.period == "month":
            return f"{obj.date} au {obj.date + relativedelta(months=1) - relativedelta(days=1)}"
        if obj.period == "week":
            return f"{obj.date} au {obj.date + relativedelta(days=6)}"
        return f"{obj.date} (jour unique)"


@admin.register(Stat)
class StatAdmin(BaseStatAdmin):
    list_display = BaseStatAdmin.list_display + ("name", "value")
    list_filter = BaseStatAdmin.list_filter + ("name",)


@admin.register(ForumStat)
class ForumStatAdmin(BaseStatAdmin):
    list_display = BaseStatAdmin.list_display + ("forum", "visits", "entry_visits", "time_spent")
    list_filter = BaseStatAdmin.list_filter + (ForumWithStatsFilter,)
    raw_id_fields = ("forum",)


@admin.register(DocumentationStat)
class DocumentionStatAdmin(BaseStatAdmin):
    list_display = BaseStatAdmin.list_display + ("content_type", "object_id", "visits", "entry_visits", "time_spent")
    list_filter = BaseStatAdmin.list_filter + (DocumentationContentTypeFilter,)
