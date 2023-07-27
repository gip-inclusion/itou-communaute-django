from django.contrib import messages
from django.urls import reverse
from machina.apps.forum_moderation.views import TopicDeleteView as BaseTopicDeleteView


class TopicDeleteView(BaseTopicDeleteView):
    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse("pages:home")
