from haystack import indexes

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True,
        use_template=True,
        template_name="forum_search/post_text.txt",
    )

    poster = indexes.IntegerField(model_attr="poster_id", null=True)
    poster_name = indexes.CharField()

    forum = indexes.IntegerField(model_attr="topic__forum_id")
    forum_slug = indexes.CharField()
    forum_name = indexes.CharField()

    topic = indexes.IntegerField(model_attr="topic_id")
    topic_slug = indexes.CharField()
    topic_subject = indexes.CharField()

    created = indexes.DateTimeField(model_attr="created")
    updated = indexes.DateTimeField(model_attr="updated")

    def get_model(self):
        return Post

    def get_updated_field(self):
        return "updated"

    def prepare_poster_name(self, obj):
        return obj.poster_display_name

    def prepare_forum_slug(self, obj):
        return obj.topic.forum.slug

    def prepare_forum_name(self, obj):
        return obj.topic.forum.name

    def prepare_topic_slug(self, obj):
        return obj.topic.slug

    def prepare_topic_subject(self, obj):
        return obj.topic.subject

    def index_queryset(self, using=None):
        return Post.objects.exclude(approved=False).exclude(topic__forum__kind=Forum_Kind.PRIVATE_FORUM)

    def read_queryset(self, using=None):
        return self.index_queryset(using=using).select_related("topic", "poster")


class ForumIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(
        document=True,
        use_template=True,
        template_name="forum_search/forum_text.txt",
    )

    forum = indexes.IntegerField(model_attr="id")
    forum_slug = indexes.CharField()
    forum_name = indexes.CharField()
    forum_description = indexes.CharField()
    forum_updated = indexes.DateTimeField(model_attr="updated")

    def get_model(self):
        return Forum

    def get_updated_field(self):
        return "updated"

    def prepare_forum_slug(self, obj):
        return obj.slug

    def prepare_forum_name(self, obj):
        return obj.name

    def prepare_forum_description(self, obj):
        return obj.description

    def prepare_forum_updated(self, obj):
        return obj.updated

    def index_queryset(self, using=None):
        return Forum.objects.filter(kind=Forum_Kind.PUBLIC_FORUM)

    def read_queryset(self, using=None):
        return self.index_queryset(using=using)
