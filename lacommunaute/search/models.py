from django.contrib.postgres.search import SearchVectorField
from django.db import models

from .enums import CommonIndexKind


class CommonIndex(models.Model):
    """
    A materialized view for use as a search index, grouping:
        - topics with the aggregated content of all their posts
        - public forums with a description written by trusted members of
          the community

    Because public forums have been written by trusted members, they
    carry more weight in the search rankings.
    In order to easily compare objects of different nature, the
    materialized view groups the searchable content.
    The id and kind fields trace back to the original object.

    To increase search performance, the indexed documents tsvector is
    denormalized into the _ts field.
    """

    id = models.UUIDField(primary_key=True, editable=False, verbose_name="ID")
    kind = models.CharField(
        editable=False,
        max_length=32,
        choices=CommonIndexKind.choices,
    )
    title = models.CharField(
        max_length=255,  # max(forum.name.length, topic.subject.length)
        editable=False,
    )
    content = models.TextField(editable=False, blank=True)
    content_ts = SearchVectorField(editable=False, blank=True)
    forum_id = models.PositiveBigIntegerField(editable=False)
    forum_slug = models.CharField(editable=False, max_length=255)
    forum_updated = models.DateTimeField(editable=False)
    topic_id = models.PositiveBigIntegerField(editable=False)
    topic_slug = models.CharField(editable=False, max_length=255)

    class Meta:
        managed = False
