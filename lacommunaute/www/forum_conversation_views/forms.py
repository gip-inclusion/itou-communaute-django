from django import forms
from machina.apps.forum_conversation.forms import TopicForm

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic


class TopicJobOfferForm(TopicForm):
    jobname = forms.CharField(
        label="Intitulé du poste",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Intitulé du poste"}),
    )
    company = forms.CharField(
        label="Structure",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Nom de la structure"}),
    )
    jobdescription = forms.CharField(
        label="Description du poste",
        required=True,
        widget=forms.Textarea(attrs={"placeholder": "Description du poste"}),
    )

    subject = forms.CharField(widget=forms.HiddenInput(), required=False)
    content = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        self.cleaned_data["subject"] = self.cleaned_data.get("jobname")
        company = self.cleaned_data.get("company")
        jobdescription = self.cleaned_data.get("jobdescription")
        self.cleaned_data["content"] = f"Structure : {company}\n\nDescription du poste :\n{jobdescription}"
        # vincentporte - weird point - createtopic method required string
        self.cleaned_data["topic_type"] = str(Topic.TOPIC_JOBOFFER)
        return super().clean()

    def save(self, commit=True, *args, **kwargs):
        self.instance.poster = self.user
        self.instance.forum = self.forum
        return super().save(commit, *args, **kwargs)
