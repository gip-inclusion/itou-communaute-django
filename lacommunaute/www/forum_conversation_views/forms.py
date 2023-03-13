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


class PostJobOfferForm(PostForm):
    phone = forms.CharField(
        label="Téléphone",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Numéro de téléphone"}),
    )
    message = forms.CharField(
        label="message", required=True, widget=forms.Textarea(attrs={"placeholder": "Description du poste"})
    )
    username = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "Adresse email"}),
    )
    content = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        phone = self.cleaned_data.get("phone")
        username = self.cleaned_data.get("username")
        message = self.cleaned_data.get("message")
        self.cleaned_data["content"] = f"Message :\n{message}\n\nTéléphone : {phone}"
        if self.user.is_anonymous:
            self.cleaned_data["content"] += f"\nEmail : {username}"
        else:
            self.cleaned_data["content"] += f"\nEmail : {self.user.email}"
        return super().clean()
