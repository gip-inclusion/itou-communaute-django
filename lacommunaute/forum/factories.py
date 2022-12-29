from machina.test.factories.forum import ForumFactory as BaseForumFactory

from lacommunaute.forum.models import Forum


class ForumFactory(BaseForumFactory):
    type = Forum.FORUM_POST
