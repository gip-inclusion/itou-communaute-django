from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import BooleanField, Count, ExpressionWrapper, Q

from lacommunaute.forum.models import Forum
from lacommunaute.metabase.models import ForumTable


class Command(BaseCommand):
    help = "Extracts data for the metabase"

    def truncate_forum_tables(self):
        ForumTable.objects.all().delete()

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

    def handle(self, *args, **options):
        extracted_at = datetime.now()

        self.truncate_forum_tables()
        self.extract_forum_tables(extracted_at)

        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
