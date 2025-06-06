from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from machina.apps.forum_member.admin import ForumProfileAdmin
from machina.core.db.models import get_model


ForumProfile = get_model("forum_member", "ForumProfile")


class HasCVFilter(admin.SimpleListFilter):
    title = "A un CV"
    parameter_name = "has_cv"

    def lookups(self, request, model_admin):
        return (("yes", "Oui"), ("no", "Non"))

    def queryset(self, request, queryset):
        conditions = Q(cv__isnull=True) | Q(cv="")
        value = self.value()
        if value == "yes":
            return queryset.exclude(conditions)
        if value == "no":
            return queryset.filter(conditions)
        return queryset


class HasLinkedInFilter(admin.SimpleListFilter):
    title = "A un lien LinkedIn"
    parameter_name = "has_linkedin"

    def lookups(self, request, model_admin):
        return (("yes", "Oui"), ("no", "Non"))

    def queryset(self, request, queryset):
        value = self.value()
        conditions = Q(linkedin__isnull=True) | Q(linkedin="")
        if value == "yes":
            return queryset.exclude(conditions)
        if value == "no":
            return queryset.filter(conditions)
        return queryset


class CommuForumProfileAdmin(ForumProfileAdmin):
    list_display = ("id", "user", "search", "region", "cv_display", "linkedin_display")
    list_filter = (
        "search",
        HasCVFilter,
        HasLinkedInFilter,
        "region",
    )

    @admin.display(description="CV")
    def cv_display(self, instance):
        if instance.cv:
            return format_html(
                "<a href='{}' target='_blank'>Télécharger le CV</a>",
                instance.cv.url,
            )

    @admin.display(description="LinkedIn")
    def linkedin_display(self, instance):
        if instance.linkedin:
            return format_html('<a href="{}">Lien du profil LK</a>', instance.linkedin)


admin.site.unregister(ForumProfile)
admin.site.register(ForumProfile, CommuForumProfileAdmin)
