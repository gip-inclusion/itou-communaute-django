import logging

from django.shortcuts import render
from django.views.generic import ListView
from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model("forum", "Forum")

logger = logging.getLogger(__name__)


class HomeListView(ListView):
    template_name = "pages/home.html"
    queryset = Forum.objects.filter(is_highlighted=True)
    context_object_name = "forums"


def contact(request):
    return render(request, "pages/contact.html")


def statistiques(request):

    # Visibility Tree is used to check forum permissions
    ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
    content_tree = ForumVisibilityContentTree.from_forums(
        request.forum_permission_handler.forum_list_filter(
            Forum.objects.all(),
            request.user,
        ),
    )

    forums_stats = []
    for node in content_tree.top_nodes:
        stats = node.obj.get_stats(7)
        forum_stats = {
            "name": node.obj.name,
            "posts_count": node.posts_count,
            "topics_count": node.topics_count,
            "members_count": stats["members"][-1],
            "stats": stats,
        }
        forums_stats.append(forum_stats)

    return render(request, "pages/statistiques.html", context={"forums_stats": forums_stats})


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
