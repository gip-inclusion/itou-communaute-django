import sys

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from taggit.models import TaggedItem

from lacommunaute.documentation.models import Category, Document
from lacommunaute.forum.models import Forum


def create_categories_from_catforums():
    # TODO next :
    # add redirections when get_absolute_url is setup
    transpo_dict = {}

    for forum in Forum.objects.filter(type=1, level=0):
        category = Category.objects.create(
            name=forum.name,
            short_description=forum.short_description,
            description=forum.description,
            image=forum.image,
        )
        transpo_dict[forum] = category

    return transpo_dict


def create_document_from_forums(category_transpo_dict):
    # TODO next :
    # add redirections when get_absolute_url is setup
    # migrate UpVotes

    forum_content_type = ContentType.objects.get_for_model(Forum)
    document_content_type = ContentType.objects.get_for_model(Document)
    transpo_dict = {}

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
        TaggedItem.objects.filter(content_type=forum_content_type, object_id=forum.id).update(
            content_type=document_content_type, object_id=document.id
        )
        transpo_dict[forum] = document

    return transpo_dict


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

        ## TODO next : migrate Ratings, Topics and Stats

        deleted_forums = del_forums(category_transpo_dict, document_transpo_dict)
        sys.stdout.write(f"{deleted_forums} forums deleted\n")

        sys.stdout.write("that's all folks!")
        sys.stdout.flush()
