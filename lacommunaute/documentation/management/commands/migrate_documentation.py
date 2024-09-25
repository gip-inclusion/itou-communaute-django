import sys

from django.contrib.contenttypes.models import ContentType
from django.contrib.redirects.models import Redirect
from django.core.management.base import BaseCommand
from taggit.models import TaggedItem

from lacommunaute.documentation.models import Category, Document, DocumentRating
from lacommunaute.forum.models import Forum, ForumRating
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.stats.models import DocumentationStat, ForumStat


def create_categories_from_catforums():
    transpo_dict = {}
    redirections = []

    for forum in Forum.objects.filter(type=1, level=0):
        category = Category.objects.create(
            name=forum.name,
            short_description=forum.short_description,
            description=forum.description,
            image=forum.image,
        )
        redirections.append(
            Redirect(site_id=1, old_path=forum.get_absolute_url(), new_path=category.get_absolute_url())
        )
        print(f"{category} created")
        transpo_dict[forum] = category

    Redirect.objects.bulk_create(redirections)

    return transpo_dict


def create_document_from_forums(category_transpo_dict):
    forum_content_type = ContentType.objects.get_for_model(Forum)
    document_content_type = ContentType.objects.get_for_model(Document)
    transpo_dict = {}
    redirections = []

    for forum in Forum.objects.filter(parent__type=1):
        document = Document.objects.create(
            name=forum.name,
            short_description=forum.short_description,
            description=forum.description,
            image=forum.image,
            category=category_transpo_dict[forum.parent],
            partner=forum.partner,
            certified=forum.certified,
        )
        UpVote.objects.filter(content_type=forum_content_type, object_id=forum.id).update(
            content_type=document_content_type, object_id=document.id
        )
        TaggedItem.objects.filter(content_type=forum_content_type, object_id=forum.id).update(
            content_type=document_content_type, object_id=document.id
        )
        redirections.append(
            Redirect(site_id=1, old_path=forum.get_absolute_url(), new_path=document.get_absolute_url())
        )
        transpo_dict[forum] = document

    Redirect.objects.bulk_create(redirections)

    return transpo_dict


def migrate_ratings(document_transpo_dict):
    document_ratings = [
        DocumentRating(
            document=document_transpo_dict[rating.forum],
            session_id=rating.session_id,
            rating=rating.rating,
            user=rating.user,
            created_at=rating.created,
            updated_at=rating.updated,
        )
        for rating in ForumRating.objects.all()
    ]
    DocumentRating.objects.bulk_create(document_ratings)
    ForumRating.objects.all().delete()


def migrate_topics(document_transpo_dict):
    main_forum = Forum.objects.get_main_forum()

    for forum, document in document_transpo_dict.items():
        topics = Topic.objects.filter(forum=forum)
        sys.stdout.write(f"*** {len(topics)} topics to migrate from {forum} ({forum.id}) to {main_forum}\n")

        for topic in topics:
            topic.document = document
            topic.forum = main_forum
            topic.save()
        forum.save()


def migrate_stats(category_transpo_dict, document_transpo_dict):
    category_content_type = ContentType.objects.get_for_model(Category)
    document_content_type = ContentType.objects.get_for_model(Document)
    documentation_stats = []

    for forum, category in category_transpo_dict.items():
        forum_stats = ForumStat.objects.filter(forum=forum)
        documentation_stats += [
            DocumentationStat(
                content_type=category_content_type,
                object_id=category.id,
                date=stat.date,
                period=stat.period,
                visits=stat.visits,
                entry_visits=stat.entry_visits,
                time_spent=stat.time_spent,
            )
            for stat in forum_stats
        ]

    for forum, document in document_transpo_dict.items():
        forum_stats = ForumStat.objects.filter(forum=forum)
        documentation_stats += [
            DocumentationStat(
                content_type=document_content_type,
                object_id=document.id,
                date=stat.date,
                period=stat.period,
                visits=stat.visits,
                entry_visits=stat.entry_visits,
                time_spent=stat.time_spent,
            )
            for stat in forum_stats
        ]

    DocumentationStat.objects.bulk_create(documentation_stats)


def del_forums(category_transpo_dict, document_transpo_dict):
    forums_to_delete = list(category_transpo_dict.keys()) + list(document_transpo_dict.keys())
    return Forum.objects.filter(pk__in=[forum.pk for forum in forums_to_delete]).delete()


class Command(BaseCommand):
    help = "migration des forums de fiches pratiques vers la documentation"

    def handle(self, *args, **options):
        sys.stdout.write("let's go!\n")

        category_transpo_dict = create_categories_from_catforums()
        sys.stdout.write("Categories created\n")

        document_transpo_dict = create_document_from_forums(category_transpo_dict)
        sys.stdout.write("Documents created\n")

        migrate_ratings(document_transpo_dict)
        sys.stdout.write("Ratings migrated\n")

        migrate_topics(document_transpo_dict)
        sys.stdout.write("Topics migrated\n")

        migrate_stats(category_transpo_dict, document_transpo_dict)
        sys.stdout.write("Stats migrated\n")

        deleted_forums = del_forums(category_transpo_dict, document_transpo_dict)
        sys.stdout.write(f"{deleted_forums} forums deleted\n")

        sys.stdout.write("that's all folks!")
        sys.stdout.flush()
