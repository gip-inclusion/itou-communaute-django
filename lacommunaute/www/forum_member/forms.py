from django import forms


class JoinForumForm(forms.Form):
    invitation_token = forms.HiddenInput()

    def join_forum(self):
        pass
