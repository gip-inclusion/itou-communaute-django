import factory

from lacommunaute.metabase.models import ForumTable


class ForumTableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForumTable
