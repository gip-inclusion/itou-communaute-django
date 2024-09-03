from django.views.generic import DetailView, ListView

from lacommunaute.partner.models import Partner


class PartnerListView(ListView):
    model = Partner
    template_name = "partner/list.html"
    context_object_name = "partners"
    paginate_by = 8 * 3

