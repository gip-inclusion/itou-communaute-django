from django.views.generic import DetailView, ListView

from lacommunaute.forum.models import Forum
from lacommunaute.partner.models import Partner
from lacommunaute.utils.perms import forum_visibility_content_tree_from_forums


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
        context["sub_forums"] = forum_visibility_content_tree_from_forums(
            self.request, Forum.objects.filter(partner=self.object)
        )
        return context
