import hashlib
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db.models import BooleanField, Count, ExpressionWrapper, OuterRef, Q, Subquery

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Post
from lacommunaute.metabase.models import ForumTable, PostTable
from lacommunaute.users.models import User


class Command(BaseCommand):
    help = "Extracts data for the metabase"

    def add_arguments(self, parser):
        parser.add_argument("--batch_size", type=int, default=1000, help="Batch size for post extraction")

    def truncate_forum_tables(self):
        ForumTable.objects.all().delete()

    def truncate_post_tables(self):
        PostTable.objects.all().delete()

    def extract_forum_tables(self, extracted_at):
        TYPE_CHOICES_DICT = {item[0]: item[1] for item in Forum.TYPE_CHOICES}
        forum_tables = []
        for forum in (
            Forum.objects.annotate(
                short_description_boolean=ExpressionWrapper(
                    Q(short_description__isnull=False), output_field=BooleanField()
                )
            )
            .annotate(description_boolean=ExpressionWrapper(Q(description__isnull=False), output_field=BooleanField()))
            .annotate(upvotes_count=Count("upvotes"))
            .select_related("parent")
        ):
            forum_tables.append(
                ForumTable(
                    name=forum.name,
                    kind=forum.kind,
                    type=TYPE_CHOICES_DICT.get(forum.type),
                    short_description_boolean=forum.short_description_boolean,
                    description_boolean=forum.description_boolean,
                    parent_name=forum.parent.name if forum.parent else None,
                    direct_topics_count=forum.direct_topics_count,
                    upvotes_count=forum.upvotes_count,
                    last_post_at=forum.last_post_on,
                    last_updated_at=forum.created,
                    extracted_at=extracted_at,
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Extracted {len(forum_tables)} forums."))

        ForumTable.objects.bulk_create(forum_tables)
        self.stdout.write(self.style.SUCCESS("Forums extracted."))

    def extract_post_tables(self, extracted_at, batch_size):
        def _resolve_analytics_username(post):
            if post.poster:
                return post.poster.username
            elif post.known_user:
                return post.known_user
            elif post.username:
                # hash email to avoid storing it in the analytics database
                return hashlib.sha256(post.username.encode("utf-8")).hexdigest()
            raise CommandError(f"No username found for post {post.id}")

        post_tables = []
        known_user_subquery = User.objects.filter(email=OuterRef("username")).values("username")[:1]
        for post in (
            Post.objects.all()
            .annotate(known_user=Subquery(known_user_subquery))
            .select_related("topic", "topic__forum", "poster", "certified_post", "certified_post__user")
            .prefetch_related("upvotes", "attachments", "topic__tags")
        ):
            post_tables.append(
                PostTable(
                    subject=post.topic.subject,
                    subject_likes_count=post.topic.likers.count(),
                    forum_name=post.topic.forum.name,
                    poster=_resolve_analytics_username(post),
                    is_anonymous_post=True if post.username else False,
                    certifier=post.certified_post.user.username if post.is_certified else None,
                    post_upvotes_count=post.upvotes.count(),
                    attachments_count=post.attachments.count(),
                    tags_list=", ".join(post.topic.tags.values_list("name", flat=True)),
                    approved_boolean=post.approved,
                    topic_created_at=post.topic.created,
                    post_created_at=post.created,
                    post_position_in_topic=post.position,
                    updates_count=post.updates_count,
                    post_last_updated_at=post.updated,
                    extracted_at=extracted_at,
                )
            )

            if len(post_tables) % batch_size == 0:
                self.stdout.write(self.style.SUCCESS(f"Extracted {len(post_tables)} posts."))
                PostTable.objects.bulk_create(post_tables)
                post_tables = []

        if post_tables:
            self.stdout.write(self.style.SUCCESS(f"Extracted {len(post_tables)} posts."))
            PostTable.objects.bulk_create(post_tables)

        self.stdout.write(self.style.SUCCESS("Posts extracted."))

    def handle(self, batch_size=1000, *args, **options):
        extracted_at = datetime.now()

        self.truncate_forum_tables()
        self.truncate_post_tables()

        self.extract_forum_tables(extracted_at)
        self.extract_post_tables(extracted_at, batch_size)

        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
