from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from lacommunaute.surveys.forms import DSPForm
from lacommunaute.surveys.models import DSP


class DSPCreateView(LoginRequiredMixin, CreateView):
    model = DSP
    template_name = "surveys/dsp_form.html"
    form_class = DSPForm

    def get_recommendations(self):
        return {
            "Recommandations": "Parcours SIAE",
        }

    def get_success_url(self):
        return reverse_lazy("surveys:dsp_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.recommendations = self.get_recommendations()
        return super().form_valid(form)


class DSPDetailView(LoginRequiredMixin, DetailView):
    model = DSP
    template_name = "surveys/dsp_detail.html"

    def get_queryset(self):
        return DSP.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recommendations"] = self.object.recommendations
        context["form"] = DSPForm(instance=self.object)
        return context
