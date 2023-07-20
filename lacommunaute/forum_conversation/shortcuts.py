from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Exists, OuterRef, Prefetch, Q, QuerySet

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.models import User


# vincentporte - setup outside models.py to avoid circular imports
def get_posts_of_a_topic_except_first_one(topic: Topic, user: User) -> QuerySet[Post]:
    first_post_pk = topic.first_post.pk if topic.first_post else None

    qs = topic.posts.exclude(Q(approved=False) | Q(pk=first_post_pk))

    qs = qs.prefetch_related(
        Prefetch("attachments"),
        Prefetch("poster__forum_profile"),
    )
    qs = qs.select_related("poster", "updated_by", "topic", "topic__forum", "certified_post")

    if user.is_authenticated:
        qs = qs.annotate(
            upvotes_count=Count("upvotes"),
            has_upvoted=Exists(
                UpVote.objects.filter(
                    object_id=OuterRef("pk"),
                    voter=user,
                    content_type_id=ContentType.objects.get_for_model(qs.model).id,
                )
            ),
        )
    else:
        qs = qs.annotate(
            upvotes_count=Count("upvotes"),
        )
    return qs.order_by("created")


def can_certify_post(forum, user):
    return (
        user.is_authenticated
        and forum.kind == Forum_Kind.PUBLIC_FORUM
        and (user.groups.filter(forum=forum).exists() or user.is_staff)
    )
