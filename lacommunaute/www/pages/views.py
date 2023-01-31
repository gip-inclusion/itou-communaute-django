import logging

from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.views.generic.base import TemplateView

from lacommunaute.forum_conversation.forum_polls.models import TopicPollVote
from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.models import User
from lacommunaute.utils.stats import count_objects_per_period, format_counts_of_objects_for_timeline_chart


logger = logging.getLogger(__name__)


def contact(request):
    return render(request, "pages/contact.html")


class StatistiquesPageView(TemplateView):
    template_name = "pages/statistiques.html"

    def get_context_data(self, **kwargs):
        datas = (
            count_objects_per_period(User.objects.annotate(period=TruncMonth("date_joined")), "users")
            + count_objects_per_period(Topic.objects.annotate(period=TruncMonth("created")), "topics")
            + count_objects_per_period(Post.objects.annotate(period=TruncMonth("created")), "posts")
            + count_objects_per_period(UpVote.objects.annotate(period=TruncMonth("created_at")), "upvotes")
            + count_objects_per_period(TopicPollVote.objects.annotate(period=TruncMonth("timestamp")), "pollvotes")
        )

        context = super().get_context_data(**kwargs)
        context["stats"] = format_counts_of_objects_for_timeline_chart(datas)
        return context


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
