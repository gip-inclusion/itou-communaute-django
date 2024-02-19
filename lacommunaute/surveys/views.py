from collections import defaultdict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from lacommunaute.surveys.forms import DSPForm
from lacommunaute.surveys.models import DSP


class DSPCreateView(CreateView):
    model = DSP
    template_name = "surveys/dsp_form.html"
    form_class = DSPForm

    def get_success_url(self):
        return reverse_lazy("surveys:dsp_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DSPDetailView(LoginRequiredMixin, DetailView):
    model = DSP
    template_name = "surveys/dsp_detail.html"

    def get_queryset(self):
        return DSP.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recommendations = defaultdict(list)
        for recommandation in self.object.recommendations.all():
            recommendations[recommandation.category].append(recommandation)
        context["global_recommendations"] = recommendations.pop("Général", [])
        context["grouped_recommendations"] = recommendations.items()
        dsp_fields = {}
        for field in DSP.CATEGORIES:
            modelfield = DSP._meta.get_field(field)
            display_method = getattr(self.object, f"get_{field}_display")
            dsp_fields[modelfield.verbose_name] = display_method()
        context["dsp_fields"] = dsp_fields
        return context
