from django import forms

from lacommunaute.forum.models import Forum


class ForumForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ["name", "short_description", "description"]
