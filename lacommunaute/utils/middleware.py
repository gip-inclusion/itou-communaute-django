from django.utils.deprecation import MiddlewareMixin
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum


ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")

# session key
UPPER_VISIBLE_FORUMS = "upper_visible_forums"


def store_upper_visible_forums(request, nodes):
    request.session[UPPER_VISIBLE_FORUMS] = [
        {
            "name": node.obj.name,
            "slug": node.obj.slug,
            "pk": node.obj.id,
        }
        for node in nodes
    ]


class VisibleForumsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        forum_visibility_content_tree = request.session.get(UPPER_VISIBLE_FORUMS, None)
        if not forum_visibility_content_tree:
            forum_visibility_content_tree = ForumVisibilityContentTree.from_forums(
                request.forum_permission_handler.forum_list_filter(
                    Forum.objects.exclude(type=Forum.FORUM_CAT),
                    request.user,
                ),
            )
            store_upper_visible_forums(request, forum_visibility_content_tree.top_nodes)
