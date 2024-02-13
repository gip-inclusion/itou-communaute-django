from django.contrib import admin

from lacommunaute.forum_moderation.models import BlockedDomainName, BlockedEmail


@admin.register(BlockedEmail)
class BlockedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "reason")
    list_filter = ("reason",)


@admin.register(BlockedDomainName)
class BlockedDomainNameAdmin(admin.ModelAdmin):
    list_display = ("domain", "created", "reason")
    list_filter = ("reason",)
