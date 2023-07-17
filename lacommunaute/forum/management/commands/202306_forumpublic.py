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


def update_topics(
    forum_id_list: List[int],
    new_forum: Forum,
) -> None:
    print("Mise à jour des topics")
    for forum in Forum.objects.filter(id__in=forum_id_list):
        print(f"/n**** Forum: {forum}")
        for topic in Topic.objects.filter(forum=forum):
            print(f"Topic: {topic}")
            topic.tags.add(forum.name)
            topic.forum = new_forum
            topic.save()
            print(f" >> moved from {forum} to {topic.forum}")


def add_forums_redirections(forum_id_list: List[int], new_forum: Forum, site: Site) -> None:
    print("Ajout des redirections")
    redirections = Redirect.objects.bulk_create(
        [
            Redirect(
                site=site,
                old_path=f"/forum/{forum.slug}-{forum.id}/",
                new_path=f"/forum/{new_forum.slug}-{new_forum.id}/",
            )
            for forum in Forum.objects.filter(id__in=forum_id_list)
        ]
    )
    print(f"redirections créées: {redirections}")


def delete_forums(forum_id_list: List[int]) -> None:
    print("Suppression des anciens forums publics")
    forums = Forum.objects.filter(id__in=forum_id_list).delete()
    print(f"{forums[0]} objets supprimés: {forums[1]}")


def delete_unapproved_topics() -> None:
    print("Suppression des topics non approuvés")
    topics = Topic.objects.filter(approved=False).delete()
    print(f"{topics[0]} objets supprimés: {topics[1]}")


class Command(BaseCommand):
    help = "réorganisation des forums publics"

    def handle(self, *args, **options):
        delete_unapproved_topics()

        create_tags(public_forums_id_list)

        forum = create_forum()
        update_topics(public_forums_id_list, forum)
        add_forums_redirections(public_forums_id_list, forum, Site.objects.get(id=site_id))
        delete_forums(public_forums_id_list)

        print("Terminé")
