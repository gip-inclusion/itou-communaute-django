from django import forms


class JoinForumForm(forms.Form):
    invitation_token = forms.HiddenInput()

    def join_forum(self):
        if not self.forum.members_group.user_set.filter(id=self.user.id).exists():
            self.forum.members_group.user_set.add(self.user)
