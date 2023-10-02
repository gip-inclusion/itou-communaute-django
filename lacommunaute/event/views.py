import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse
from django.views.generic.dates import MonthArchiveView
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


class EventMonthArchiveView(MonthArchiveView):
    allow_future = True
    date_field = "date"
    queryset = Event.objects.all()
    month_format = "%m"
    year_format = "%Y"

    def get_month(self):
        try:
            month = super().get_month()
        except Http404:
            month = datetime.now().strftime(self.get_month_format())
        return month

    def get_year(self):
        try:
            year = super().get_year()
        except Http404:
            year = datetime.now().strftime(self.get_year_format())
        return year
