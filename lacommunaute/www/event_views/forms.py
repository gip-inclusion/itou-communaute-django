from django import forms
from django.utils import timezone

from lacommunaute.event.models import Event


class EventModelForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "date", "time", "end_date", "end_time", "location", "description"]
        date = forms.DateField(widget=forms.SelectDateWidget)
        time = forms.TimeField(widget=forms.TimeInput)
        end_date = forms.DateField(widget=forms.SelectDateWidget)
        end_time = forms.TimeField(widget=forms.TimeInput)

    # add controls on dates and times
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")

        if date and time and end_date and end_time:
            if date > end_date:
                self.add_error("end_date", "La date de fin doit être après la date de début.")
            elif date == end_date and time > end_time:
                self.add_error("end_time", "L'heure de fin doit être après l'heure de début.")
            # date and time are not in the past
            if date < timezone.now().date():
                self.add_error("date", "La date ne peut pas être dans le passé.")
            if end_date < timezone.now().date():
                self.add_error("end_date", "La date ne peut pas être dans le passé.")


# TODO vincentporte
# ajouter dates et times picker
# ajouter l'upload d'image (en attente dans le js)
# renommer date et time (ambiguite avec python, mais gros refactor js)
