from django.contrib import admin

from lacommunaute.forum_upvote.models import UpVote


class UpVoteAdmin(admin.ModelAdmin):
    list_display = ("voter", "post", "created_at")
    raw_id_fields = (
        "voter",
        "post",
    )


admin.site.register(UpVote, UpVoteAdmin)
