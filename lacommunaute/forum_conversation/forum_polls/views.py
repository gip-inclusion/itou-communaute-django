import logging

from django.template.response import TemplateResponse
from machina.apps.forum_conversation.forum_polls.views import TopicPollVoteView as BaseTopicPollVoteView
from machina.core.loading import get_class

from lacommunaute.forum_conversation.forum_polls.models import TopicPollVote


logger = logging.getLogger(__name__)


PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class TopicPollVoteView(BaseTopicPollVoteView):
    def form_valid(self, form):
        """Handles a valid form."""
        user_kwargs = (
            {"voter": self.request.user}
            if self.request.user.is_authenticated
            else {"anonymous_key": self.request.user.forum_key}
        )

        if self.object.user_changes:
            # If user changes are allowed for this poll, all the poll associated with the current
            # user must be deleted.
            TopicPollVote.objects.filter(poll_option__poll=self.object, **user_kwargs).delete()

        options = form.cleaned_data["options"]
        for option in options:
            TopicPollVote.objects.create(poll_option=option, **user_kwargs)

        track_handler.mark_topic_read(self.object.topic, self.request.user)

        return TemplateResponse(
            request=self.request,
            template="forum_conversation/forum_polls/topic_list_poll_detail.html",
            context={"poll": self.object},
        )
