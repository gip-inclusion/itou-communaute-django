from machina.apps.forum.admin import ForumAdmin as BaseForumAdmin


class ForumAdmin(BaseForumAdmin):
    fieldsets = BaseForumAdmin.fieldsets
    fieldsets[0][1]["fields"] += ("short_description",)
    fieldsets[1][1]["fields"] += (
        "members_group",
        "invitation_token",
        "kind",
    )
