from django.views.generic import DetailView, ListView
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.partner.models import Partner


ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")


class PartnerListView(ListView):
    model = Partner
    template_name = "partner/list.html"
    context_object_name = "partners"
    paginate_by = 8 * 3


class PartnerDetailView(DetailView):
    model = Partner
    template_name = "partner/detail.html"
    context_object_name = "partner"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sub_forums"] = ForumVisibilityContentTree.from_forums(
            self.request.forum_permission_handler.forum_list_filter(
                Forum.objects.filter(partner=self.object),
                self.request.user,
            ),
        )
        return context
