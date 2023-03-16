from django.contrib import admin

from lacommunaute.forum_upvote.models import CertifiedPost, UpVote


class UpVoteAdmin(admin.ModelAdmin):

    list_display = ("voter", "post", "created_at")
    raw_id_fields = (
        "voter",
        "post",
    )


class CertifiedPostAdmin(admin.ModelAdmin):

    list_display = ("topic", "post", "user")
    raw_id_fields = (
        "topic",
        "post",
        "user",
    )


admin.site.register(CertifiedPost, CertifiedPostAdmin)
admin.site.register(UpVote, UpVoteAdmin)
