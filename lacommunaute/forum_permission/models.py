from machina.apps.forum_permission.abstract_models import (
    AbstractForumPermission,
    AbstractGroupForumPermission,
    AbstractUserForumPermission,
)


class ForumPermission(AbstractForumPermission):
    pass


class GroupForumPermission(AbstractGroupForumPermission):
    pass


class UserForumPermission(AbstractUserForumPermission):
    pass
