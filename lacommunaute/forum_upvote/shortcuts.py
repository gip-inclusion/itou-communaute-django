def can_certify_post(forum, user):
    return (
        user.is_authenticated and not forum.is_private and (user.groups.filter(forum=forum).exists() or user.is_staff)
    )
