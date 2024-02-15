from datetime import datetime

from django.urls import reverse
from django.utils.timezone import now, timedelta
from taggit.models import TaggedItem

from lacommunaute.forum_conversation.models import Topic
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import EmailSentTrack, TagsNotification
from lacommunaute.users.models import User


def last_notification(kind=None) -> datetime:
    return getattr(EmailSentTrack.objects.filter(kind=kind).last(), "created", now() - timedelta(days=5))


def collect_first_replies():
    return [
        (
            topic.get_absolute_url(with_fqdn=True),
            topic.subject,
            topic.mails_to_notify(),
            topic.last_post.poster_display_name,
        )
        for topic in Topic.objects.with_first_reply(last_notification(kind=EmailSentTrackKind.FIRST_REPLY))
    ]


def collect_following_replies():
    return [
        (
            topic.get_absolute_url(with_fqdn=True),
            topic.subject,
            topic.mails_to_notify(),
            f"{topic.new_replies} nouvelle réponse"
            if topic.new_replies == 1
            else f"{topic.new_replies} nouvelles réponses",
        )
        for topic in Topic.objects.with_following_replies(last_notification(kind=EmailSentTrackKind.FOLLOWING_REPLIES))
    ]


def collect_topics_digest_for_tags():
    last_notif = last_notification(kind=EmailSentTrackKind.TAG_DIGEST)

    return [
        (
            f"{reverse('forum_conversation_extension:topics')}?tags={tag.slug}",
            f"La communauté - résumé hebdo de {tag.name}",
            TagsNotification.objects.filter(tags=tag.id, newpost=True).values_list("user__email", flat=True),
            Topic.objects.filter(tags=tag, updated__gte=last_notif).count(),
        )
        for tag in TaggedItem.tags_for(TagsNotification)
        if Topic.objects.filter(tags=tag, updated__gte=last_notif).count() > 0
    ]


def collect_new_users_for_onboarding():
    return User.objects.filter(date_joined__gte=last_notification(kind=EmailSentTrackKind.ONBOARDING))
