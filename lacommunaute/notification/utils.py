from datetime import datetime
from django.db.models import Count, F, Q
from django.utils.timezone import now, timedelta

from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.models import BouncedEmail, EmailSentTrack
from lacommunaute.users.models import User


def last_notification(kind=None) -> datetime:
    return getattr(EmailSentTrack.objects.filter(kind=kind).last(), "created", now() - timedelta(days=5))


def collect_first_replies():
    return [
        (
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{post.topic.get_absolute_url()}",
            post.topic.subject,
            post.topic.poster_email,
            post.poster_display_name,
        )
        for post in Post.objects.filter(
            created__gte=last_notification(kind=EmailSentTrackKind.FIRST_REPLY),
            approved=True,
        )
        if post.position == 2
    ]


def collect_following_replies():
    # vincentporte : assumed disapproved post are counted
    return [
        (
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{topic.get_absolute_url()}",
            topic.subject,
            topic.poster_email,
            f"{topic.new_replies} nouvelle réponse"
            if topic.new_replies == 1
            else f"{topic.new_replies} nouvelles réponses",
        )
        for topic in Topic.objects.filter(
            updated__gte=last_notification(kind=EmailSentTrackKind.FOLLOWING_REPLIES), posts_count__gte=3
        ).annotate(
            new_replies=Count(
                "posts",
                filter=Q(posts__created__gte=last_notification(kind=EmailSentTrackKind.FOLLOWING_REPLIES))
                & ~Q(posts__id=F("first_post_id")),
            )
        )
    ]


def collect_new_users_for_onboarding():
    return User.objects.filter(date_joined__gte=last_notification(kind=EmailSentTrackKind.ONBOARDING))


def should_not_be_approved(username: str) -> bool:
    """
    User model stores Inclusion Connect uuid as username, email as email
    Post model stores anonymous user email as username
    """
    if User.objects.filter(email=username).exists():
        # email is known in User model, registered user through Inclusion Connect
        return False

    if BouncedEmail.objects.filter(email=username).exists():
        return True

    # vincentporte TODO : add check for email not in User model and not in BouncedEmail model

    return False
