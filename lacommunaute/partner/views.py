from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from lacommunaute.forum.models import Forum
from lacommunaute.partner.forms import PartnerForm
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


class PartnerCreateView(UserPassesTestMixin, CreateView):
    model = Partner
    template_name = "partner/create_or_update.html"
    form_class = PartnerForm

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Créer une nouvelle page partenaire"
        context["back_url"] = reverse("partner:list")
        return context

    def get_success_url(self):
        return reverse("partner:detail", kwargs={"pk": self.object.pk, "slug": self.object.slug})
