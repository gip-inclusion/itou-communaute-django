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

    days_back = 7
    forums_stats = []
    forums_stats_totals = {"topics": [0] * days_back, "posts": [0] * days_back}
    for node in content_tree.top_nodes:
        stats = node.obj.get_stats(days_back)
        forum_stats = {
            "name": node.obj.name,
            "is_private": node.obj.is_private,  # add this because members counters make sense only if forum is private
            "posts_count": node.posts_count,
            "topics_count": node.topics_count,
            "members_count": stats["members"][-1],
            "stats": stats,
        }
        forums_stats.append(forum_stats)

        for key in ["topics", "posts"]:
            forums_stats_totals[key] = [x + y for x, y in zip(forums_stats_totals[key], stats[key])]

    if len(forums_stats) > 1:
        # added total stats as it was a forum
        forums_stats_totals["days"] = forums_stats[-1]["stats"]["days"]
        forum_stats = {
            "name": "Toutes les communautés",
            "is_private": False,
            "posts_count": forums_stats_totals["posts"][-1],
            "topics_count": forums_stats_totals["topics"][-1],
            "members_count": 0,  # The number of members is not set because a member can be a member of several forums
            "stats": forums_stats_totals,
        }
        forums_stats.append(forum_stats)

    return render(request, "pages/statistiques.html", context={"forums_stats": forums_stats})


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
