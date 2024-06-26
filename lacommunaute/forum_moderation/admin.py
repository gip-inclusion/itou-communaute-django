from django.contrib import admin

from lacommunaute.forum_moderation.models import BlockedDomainName, BlockedEmail, BlockedPost


@admin.register(BlockedEmail)
class BlockedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "reason")
    list_filter = ("reason",)


@admin.register(BlockedDomainName)
class BlockedDomainNameAdmin(admin.ModelAdmin):
    list_display = ("domain", "created", "reason")
    list_filter = ("reason",)


@admin.register(BlockedPost)
class BlockedPostAdmin(admin.ModelAdmin):
    list_display = ("username", "created", "block_reason")
    list_filter = ("block_reason",)
