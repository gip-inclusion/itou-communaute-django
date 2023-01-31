from machina.apps.forum.admin import ForumAdmin as BaseForumAdmin


class ForumAdmin(BaseForumAdmin):
    fieldsets = BaseForumAdmin.fieldsets
    fieldsets[1][1]["fields"] += (
        "members_group",
        "invitation_token",
        "is_private",
        "target_audience",
    )
