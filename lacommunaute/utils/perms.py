from machina.core.db.models import get_model


ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")


def add_public_perms_on_forum(forum):
    perms = [
        "can_see_forum",
        "can_read_forum",
        "can_start_new_topics",
        "can_reply_to_topics",
        "can_edit_own_posts",
        "can_delete_own_posts",
        "can_post_without_approval",
    ]

    anonymous_authorized_perms = [
        UserForumPermission(
            anonymous_user=True, authenticated_user=False, permission=permission, has_perm=True, forum=forum
        )
        for permission in ForumPermission.objects.filter(codename__in=perms)
    ]

    authentified_authorized_perms = [
        UserForumPermission(
            anonymous_user=False, authenticated_user=True, permission=permission, has_perm=True, forum=forum
        )
        for permission in ForumPermission.objects.filter(codename__in=perms)
    ]
    UserForumPermission.objects.bulk_create(anonymous_authorized_perms + authentified_authorized_perms)
