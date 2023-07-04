from lacommunaute.forum.enums import Kind as Forum_Kind


def can_certify_post(forum, user):
    return (
        user.is_authenticated
        and forum.kind == Forum_Kind.PUBLIC_FORUM
        and (user.groups.filter(forum=forum).exists() or user.is_staff)
    )
