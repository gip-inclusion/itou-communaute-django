from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={"placeholder": "Votre adresse email"}),
    )


class CreateUserForm(forms.Form):
    first_name = forms.CharField(label="Votre prénom", max_length=150)
    last_name = forms.CharField(label="Votre nom", max_length=150)
    email = forms.EmailField(label="Votre adresse email")
