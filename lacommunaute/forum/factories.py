import factory
from machina.core.db.models import get_model
from machina.test.factories.forum import ForumFactory as BaseForumFactory

from lacommunaute.forum.models import Forum
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import GroupFactory


ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")


class ForumFactory(BaseForumFactory):
    type = Forum.FORUM_POST
    members_group = factory.SubFactory(GroupFactory, name=factory.SelfAttribute("..name"))
    name = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=100)
    short_description = factory.Faker("sentence", nb_words=10)

    class Meta:
        skip_postgeneration_save = True

    @factory.post_generation
    def with_public_perms(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        perms = [
            "can_see_forum",
            "can_read_forum",
            "can_start_new_topics",
            "can_reply_to_topics",
            "can_edit_own_posts",
            "can_delete_own_posts",
            "can_post_without_approval",
        ]

        anonymous_authorized_perms = [
            UserForumPermission(
                anonymous_user=True, authenticated_user=False, permission=permission, has_perm=True, forum=self
            )
            for permission in ForumPermission.objects.filter(codename__in=perms)
        ]

        authentified_authorized_perms = [
            UserForumPermission(
                anonymous_user=False, authenticated_user=True, permission=permission, has_perm=True, forum=self
            )
            for permission in ForumPermission.objects.filter(codename__in=perms)
        ]
        UserForumPermission.objects.bulk_create(anonymous_authorized_perms + authentified_authorized_perms)

    @factory.post_generation
    def upvoted_by(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for user in extracted:
            UpVote.objects.create(voter=user, content_object=self)


class CategoryForumFactory(ForumFactory):
    type = Forum.FORUM_CAT

    @factory.post_generation
    def with_child(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        ForumFactory(parent=self, with_public_perms=True)
