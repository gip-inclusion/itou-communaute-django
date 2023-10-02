import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from lacommunaute.event.forms import EventModelForm
from lacommunaute.event.models import Event


logger = logging.getLogger(__name__)


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            "event:myevents",
        )


class EventCreateView(LoginRequiredMixin, SuccessUrlMixin, CreateView):
    model = Event
    form_class = EventModelForm

    def form_valid(self, form):
        form.instance.poster = self.request.user
        return super().form_valid(form)


class EventUpdateView(LoginRequiredMixin, SuccessUrlMixin, UpdateView):
    model = Event
    form_class = EventModelForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.poster == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def form_valid(self, form):
        form.instance.poster = self.request.user
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, SuccessUrlMixin, DeleteView):
    model = Event

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.poster == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


class EventListView(LoginRequiredMixin, ListView):
    model = Event

    def get_queryset(self):
        return Event.objects.filter(poster=self.request.user)


class EventDetailView(DetailView):
    model = Event
    template_name = "event/event_detail.html"


# TODO vincentporte : factoriser les EventXXXView


def calendar_data(request):
    data = {
        "items": list(
            Event.current_and_upcomings.annotate(
                year=ExtractYear("date"),
                month=ExtractMonth("date"),
                day=ExtractDay("date"),
                duration=ExtractDay(F("end_date") - F("date")) + 1,
            ).values(
                "id",
                "name",
                "color",
                "location",
                "description",
                "poster_id",
                "year",
                "month",
                "day",
                "time",
                "duration",
            )
        )
    }
    return JsonResponse(data)


# TODO vincentporte : supprimer ce pseudo endpoint au profit du passage en context des données
# dans la méthode calendar (refactor js)


def calendar(request):
    return TemplateResponse(request, "event/event_calendar.html")
