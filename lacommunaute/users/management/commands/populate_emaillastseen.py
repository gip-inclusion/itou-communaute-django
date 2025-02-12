from logging import getLogger

from django.core.management.base import BaseCommand
from django.db.models import Case, F, Value, When

from lacommunaute.event.models import Event
from lacommunaute.forum.models import ForumRating
from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.notification.models import Notification
from lacommunaute.surveys.models import DSP
from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.models import EmailLastSeen, User


logger = getLogger("commands")


def collect_users_logged_in():
    qs = (
        User.objects.exclude(last_login=None)
        .annotate(last_seen_kind=Value(EmailLastSeenKind.LOGGED))
        .values_list("email", "last_login", "last_seen_kind")
    )
    return tuple(qs)


def collect_event():
    qs = (
        Event.objects.all()
        .annotate(last_seen_kind=Value(EmailLastSeenKind.LOGGED))
        .values_list("poster__email", "created", "last_seen_kind")
    )
    return tuple(qs)


def collect_DSP():
    qs = (
        DSP.objects.all()
        .annotate(last_seen_kind=Value(EmailLastSeenKind.LOGGED))
        .values_list("user__email", "created", "last_seen_kind")
    )
    return tuple(qs)


def collect_upvote():
    qs = (
        UpVote.objects.exclude(voter=None)
        .annotate(last_seen_kind=Value(EmailLastSeenKind.LOGGED))
        .values_list("voter__email", "created_at", "last_seen_kind")
    )
    return tuple(qs)


def collect_forum_rating():
    qs = (
        ForumRating.objects.exclude(user=None)
        .annotate(last_seen_kind=Value(EmailLastSeenKind.LOGGED))
        .values_list("user__email", "created", "last_seen_kind")
    )
    return tuple(qs)


def collect_post():
    qs = Post.objects.annotate(
        email=Case(
            When(poster__isnull=False, then=F("poster__email")),
            When(poster__isnull=True, then=F("username")),
            default=Value(""),
        ),
        kind=Value(EmailLastSeenKind.POST),
    ).values_list("email", "created", "kind")
    return tuple(qs)


def collect_clicked_notifs():
    qs = (
        Notification.objects.exclude(visited_at=None)
        .annotate(last_seen_kind=Value(EmailLastSeenKind.VISITED))
        .values_list("recipient", "visited_at", "last_seen_kind")
    )
    return tuple(qs)


def collect_existing_email_last_seen(emails):
    qs = EmailLastSeen.objects.filter(email__in=emails).values_list("email", "last_seen_at", "last_seen_kind")
    return tuple(qs)


def keep_most_recent_tuple(last_seen):
    return {tup[0]: tup for tup in sorted(last_seen, key=lambda tup: (tup[0], tup[1]))}


def insert_last_seen(emails):
    obj = [
        EmailLastSeen(email=email, last_seen_at=last_seen_at, last_seen_kind=last_seen_kind)
        for email, last_seen_at, last_seen_kind in emails.values()
    ]
    return EmailLastSeen.objects.bulk_create(
        obj,
        update_fields=["last_seen_at", "last_seen_kind"],
        update_conflicts=True,
        unique_fields=["email"],
        batch_size=1000,
    )


def iterate_over_emails(collected_emails, size=1000):
    logger.info("will process %s emails", len(collected_emails))
    while batch_emails := collected_emails[:size]:
        existing_emails = collect_existing_email_last_seen([email for email, _, _ in batch_emails])
        most_recent = keep_most_recent_tuple(batch_emails + existing_emails)
        insert_last_seen(most_recent)

        collected_emails = collected_emails[size:]

        logger.info("remaining: %s", len(collected_emails))


class Command(BaseCommand):
    help = "hydratation de la table EmailLastSeen avec la date de dernière visite des emails connus"

    def handle(self, *args, **options):
        logger.info("starting to populate EmailLastSeen table")

        logger.info("processing users")
        users = collect_users_logged_in()
        iterate_over_emails(users)

        logger.info("processing events")
        events = collect_event()
        iterate_over_emails(events)

        logger.info("processing DSP")
        dsp = collect_DSP()
        iterate_over_emails(dsp)

        logger.info("processing upvotes")
        upvotes = collect_upvote()
        iterate_over_emails(upvotes)

        logger.info("processing forum ratings")
        forum_ratings = collect_forum_rating()
        iterate_over_emails(forum_ratings)

        logger.info("processing posts")
        posts = collect_post()
        iterate_over_emails(posts)

        logger.info("processing clicked notifications")
        clicked_notifs = collect_clicked_notifs()
        iterate_over_emails(clicked_notifs)

        logger.info("that's all folks!\n")
