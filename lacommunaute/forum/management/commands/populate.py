import sys

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import connection

from lacommunaute.event.factories import EventFactory
from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum_conversation.factories import AnonymousTopicFactory, PostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


class Command(BaseCommand):
    help = "hydratation d'un site de validation"

    def handle(self, *args, **options):
        UserFactory(username="communaute", password=make_password("password"))
        sys.stdout.write("superuser created\n")

        forum = ForumFactory(name="Espace d'échanges", with_public_perms=True)
        TopicFactory.create_batch(20, forum=forum, with_post=True)
        TopicFactory.create_batch(
            3, forum=forum, with_post=True, with_tags=["Pirmadienis", "Poniedziałek", "Lundi", "Montag"]
        )
        TopicFactory(forum=forum, with_post=True, with_certified_post=True)
        AnonymousTopicFactory.create_batch(2, forum=forum, with_post=True)
        PostFactory.create_batch(3, topic=TopicFactory(forum=forum, with_post=True))
        sys.stdout.write("public forum created\n")

        for i in range(1, 3):
            parent = CategoryForumFactory(with_public_perms=True, name=f"Thème {i}")
            for j in range(1, 3):
                TopicFactory.create_batch(
                    2, forum=ForumFactory(parent=parent, with_public_perms=True, name=f"Fiche {i}-{j}"), with_post=True
                )
        sys.stdout.write("documentation created\n")

        EventFactory.create_batch(5)
        sys.stdout.write("events created\n")

        # refresh materialized view
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW search_commonindex")
        sys.stdout.write("search index refreshed\n")

        sys.stdout.write("that's all folks!")
        sys.stdout.flush()
