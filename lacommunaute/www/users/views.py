from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import FormView

from lacommunaute.www.users.forms import SignUpForm


class SignUpView(FormView):

    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("pages:home")
    success_message = "Successfully signed up"  # . Please check your mailbox to complete email verification"

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
