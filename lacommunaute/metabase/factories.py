import factory

from lacommunaute.metabase.models import ForumTable, PostTable


class ForumTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForumTable


class PostTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostTable
