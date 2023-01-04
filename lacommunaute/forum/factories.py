import factory
from machina.test.factories.forum import ForumFactory as BaseForumFactory

from lacommunaute.forum.models import Forum
from lacommunaute.users.factories import GroupFactory


class ForumFactory(BaseForumFactory):
    type = Forum.FORUM_POST
    members_group = factory.SubFactory(GroupFactory, name=factory.SelfAttribute("..name"))
