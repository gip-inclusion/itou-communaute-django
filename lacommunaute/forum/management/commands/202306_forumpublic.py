from typing import List

from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from taggit.models import Tag

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Topic


public_forums_id_list = [2, 106, 69, 107, 50, 98]
new_forum_name = "Espace d'échanges"
site_id = 1


def create_tags(forum_id_list: List[int]) -> None:
    print("Création des nouveaux tags")
    return Tag.objects.bulk_create(
        [Tag(name=forum.name, slug=forum.slug) for forum in Forum.objects.filter(id__in=forum_id_list)]
    )


def create_forum() -> Forum:
    print("Création du nouveau forum public")
    forum = Forum.objects.create(name=new_forum_name, type=Forum.FORUM_POST)
    forum.move_to(Forum.objects.get(tree_id=1, level=0), "left")
    return forum


def update_topics(forum_id_list: List[int], new_forum: Forum) -> None:
    print("Mise à jour des topics")
    for forum in Forum.objects.filter(id__in=public_forums_id_list):
        for topic in Topic.objects.filter(forum=forum):
            topic.tags.add(forum.name)
            topic.forum = new_forum
            topic.save()


def add_redirections(forum_id_list: List[int], site_id: int, new_forum: Forum) -> None:
    print("Ajout des redirections")
    site = Site.objects.get(id=site_id)
    Redirect.objects.bulk_create(
        [
            Redirect(
                site=site,
                old_path=f"/forum/{forum.slug}-{forum.id}/{topic.slug}-{topic.id}",
                new_path=f"/forum/{new_forum.slug}-{new_forum.id}/{topic.slug}-{topic.id}",
            )
            for forum in Forum.objects.filter(id__in=forum_id_list)
            for topic in Topic.objects.filter(forum=forum)
        ]
    )


class Command(BaseCommand):
    help = "réorganisation des forums publics"

    def handle(self, *args, **options):
        # ajouter les nouveaux tags à partir des forums publics existants
        create_tags(public_forums_id_list)

        # ajouter le nouveau forum public
        forum = create_forum()

        # ajouter ces tags aux topics concernés
        # migrer les topics des forums publics existants vers le nouveau forum public
        update_topics(public_forums_id_list, forum)

        # ajouter les redirections des anciens forums publics vers le nouveau forum public
        add_redirections(public_forums_id_list, site_id, forum)

        # supprimer les forums publics existants
        print("Suppression des anciens forums publics")
        Forum.objects.filter(id__in=public_forums_id_list).delete()

        print("Terminé")
