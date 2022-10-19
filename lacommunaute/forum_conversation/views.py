from django.urls import reverse
from machina.apps.forum_conversation import views


class PostCreateView(views.PostCreateView):
    def get_success_url(self):
        # topic = self.get_topic()
        forum = self.get_forum()

        return (
            reverse(
                "forum:forum",
                kwargs={"pk": forum.pk, "slug": forum.slug},
            )
            # + f"?post%{topic.last_post}#{topic.last_post}"
            # # note vincentporte : design to be fixed to handle auto-positionning
        )
