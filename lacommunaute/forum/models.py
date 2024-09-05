from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from machina.apps.forum.abstract_models import AbstractForum
from machina.models import DatedModel
from storages.backends.s3boto3 import S3Boto3Storage
from taggit.managers import TaggableManager

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.partner.models import Partner
from lacommunaute.utils.validators import validate_image_size


class Forum(AbstractForum):
    kind = models.CharField(
        max_length=20, choices=Forum_Kind.choices, default=Forum_Kind.PUBLIC_FORUM, verbose_name="Type"
    )
    short_description = models.CharField(
        max_length=400, blank=True, null=True, verbose_name="Description courte (SEO)"
    )
    image = models.ImageField(
        storage=S3Boto3Storage(bucket_name=settings.AWS_STORAGE_BUCKET_NAME, file_overwrite=False),
        validators=[validate_image_size],
    )
    certified = models.BooleanField(default=False, verbose_name="Certifié par la communauté de l'inclusion")

    upvotes = GenericRelation(UpVote, related_query_name="forum")

    tags = TaggableManager()
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True, blank=True)

    objects = models.Manager()

    def get_absolute_url(self):
        return reverse(
            "forum_extension:forum",
            kwargs={
                "pk": self.pk,
                "slug": self.slug,
            },
        )

    def get_unanswered_topics(self):
        return Topic.objects.unanswered().filter(forum__in=self.get_descendants(include_self=True))

    @cached_property
    def count_unanswered_topics(self):
        return self.get_unanswered_topics().count()

    def upvotes_count(self):
        return self.upvotes.count()

    @cached_property
    def is_in_documentation_area(self):
        return (self.type == Forum.FORUM_CAT and self.get_level() == 0) or (
            self.get_level() > 0 and self.get_ancestors().first().type == Forum.FORUM_CAT
        )

    @cached_property
    def is_toplevel_discussion_area(self):
        return self == Forum.objects.filter(lft=1, level=0).first()

    def get_session_rating(self, session_key):
        return getattr(ForumRating.objects.filter(forum=self, session_id=session_key).first(), "rating", None)

    def get_average_rating(self):
        return ForumRating.objects.filter(forum=self).aggregate(models.Avg("rating"))["rating__avg"]


class ForumRating(DatedModel):
    session_id = models.CharField(max_length=40)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Notation Forum"
        verbose_name_plural = "Notations Forum"
        ordering = ("-created",)
