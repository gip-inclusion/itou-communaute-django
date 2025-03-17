from machina.core.loading import get_class


ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")


def forum_visibility_content_tree_from_forums(request, forums):
    return ForumVisibilityContentTree.from_forums(
        request.forum_permission_handler.forum_list_filter(
            forums,
            request.user,
        ),
    )
