import itertools
import random

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from machina.core.db.models import get_model
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


Forum = get_model("forum", "Forum")
Topic = get_model("forum_conversation", "Topic")
Post = get_model("forum_conversation", "Post")
ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
GroupForumPermission = get_model("forum_permission", "GroupForumPermission")


class Command(BaseCommand):
    help = "Generate Fake Contents for dev/demo/validation environments"

    def handle(self, **options):
        users = UserFactory.create_batch(5, password="password")

        forum = create_forum()
        moderators, _ = Group.objects.get_or_create(name=f"{forum.name} moderators")
        moderators.user_set.add(users[0])
        moderators.save()

        members, _ = Group.objects.get_or_create(name=f"{forum.name} members")
        for user in users[1:]:
            members.user_set.add(user)
        members.save()

        forum.members_group = members
        forum.save()

        topics = TopicFactory.create_batch(20, forum=forum, poster=users[1], type=Topic.TOPIC_POST)
        for topic, user in list(zip(topics, itertools.cycle(users))):
            PostFactory.create_batch(random.randint(3, 10), topic=topic, poster=user)

        declined = [
            "can_edit_posts",
            "can_lock_topics",
            "can_delete_posts",
            "can_move_topics",
            "can_approve_posts",
            "can_reply_to_locked_topics",
            "can_vote_in_polls",
            "can_create_polls",
            "can_post_stickies",
            "can_post_announcements",
        ]

        # anonymous
        UserForumPermission.objects.bulk_create(
            [
                UserForumPermission(
                    anonymous_user=True, authenticated_user=False, permission=permission, has_perm=False, forum=forum
                )
                for permission in ForumPermission.objects.filter(codename__in=declined)
            ]
        )
        UserForumPermission.objects.bulk_create(
            [
                UserForumPermission(
                    anonymous_user=True, authenticated_user=False, permission=permission, has_perm=True, forum=forum
                )
                for permission in ForumPermission.objects.exclude(codename__in=declined)
            ]
        )

        # authenticated
        UserForumPermission.objects.bulk_create(
            [
                UserForumPermission(
                    anonymous_user=False, authenticated_user=True, permission=permission, has_perm=False, forum=forum
                )
                for permission in ForumPermission.objects.filter(codename__in=declined)
            ]
        )
        UserForumPermission.objects.bulk_create(
            [
                UserForumPermission(
                    anonymous_user=False, authenticated_user=True, permission=permission, has_perm=True, forum=forum
                )
                for permission in ForumPermission.objects.exclude(codename__in=declined)
            ]
        )

        # moderators
        GroupForumPermission.objects.bulk_create(
            [
                GroupForumPermission(group=moderators, permission=permission, has_perm=True, forum=forum)
                for permission in ForumPermission.objects.all()
            ]
        )

        # animators
        GroupForumPermission.objects.bulk_create(
            [
                GroupForumPermission(group=members, permission=permission, has_perm=False, forum=forum)
                for permission in ForumPermission.objects.filter(codename__in=declined)
            ]
        )

        GroupForumPermission.objects.bulk_create(
            [
                GroupForumPermission(group=members, permission=permission, has_perm=True, forum=forum)
                for permission in ForumPermission.objects.exclude(codename__in=declined)
            ]
        )
