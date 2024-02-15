from machina.apps.forum_member.abstract_models import AbstractForumProfile

from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


class ForumProfile(AbstractForumProfile):
    def __str__(self):
        return get_forum_member_display_name(self.user)
