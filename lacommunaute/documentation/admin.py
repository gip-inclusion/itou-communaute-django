from django.contrib import admin

from lacommunaute.documentation.models import Category, Document, DocumentRating


class DocumentInlines(admin.TabularInline):
    model = Document
    extra = 0
    fields = ("name", "short_description")
    readonly_fields = ("name", "short_description")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    fields = ("name", "short_description", "description", "image")
    inlines = [DocumentInlines]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category", "partner")
    search_fields = ("name",)
    fields = ("name", "short_description", "description", "image", "category", "partner", "certified", "tags")


@admin.register(DocumentRating)
class DocumentRatingAdmin(admin.ModelAdmin):
    list_display = ("document", "rating", "created")
    list_filter = ("document",)
    list_display_links = ("rating",)
    raw_id_fields = ("document", "user")
