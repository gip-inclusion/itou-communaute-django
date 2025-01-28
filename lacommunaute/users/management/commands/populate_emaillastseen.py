import sys

from django.core.management.base import BaseCommand
from django.db.models import Value

from lacommunaute.event.models import Event
from lacommunaute.forum.models import ForumRating
from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.surveys.models import DSP
from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.models import EmailLastSeen, User


def collect_users_logged_in():
    qs = (
        User.objects.exclude(last_login=None)
        .annotate(kind=Value(EmailLastSeenKind.LOGGED))
        .values_list("email", "last_login", "kind")
    )
    return list(qs)


def collect_event():
    qs = (
        Event.objects.all()
        .annotate(kind=Value(EmailLastSeenKind.EVENT))
        .values_list("poster__email", "created", "kind")
    )
    return list(qs)


def collect_DSP():
    qs = DSP.objects.all().annotate(kind=Value(EmailLastSeenKind.DSP)).values_list("user__email", "created", "kind")
    return list(qs)


def collect_upvote():
    qs = (
        UpVote.objects.exclude(voter=None)
        .annotate(kind=Value(EmailLastSeenKind.UPVOTE))
        .values_list("voter__email", "created_at", "kind")
    )
    return list(qs)


def collect_forum_rating():
    qs = (
        ForumRating.objects.exclude(user=None)
        .annotate(kind=Value(EmailLastSeenKind.FORUM_RATING))
        .values_list("user__email", "created", "kind")
    )
    return list(qs)


def collect_post():
    qs_authenticated = (
        Post.objects.exclude(poster=None)
        .annotate(kind=Value(EmailLastSeenKind.POST))
        .values_list("poster__email", "created", "kind")
    )
    qs_anonymous = (
        Post.objects.filter(poster=None)
        .annotate(kind=Value(EmailLastSeenKind.POST))
        .values_list("username", "created", "kind")
    )
    return list(qs_authenticated) + list(qs_anonymous)


def collect_clicked_notifs():
    # TODO VincentPorte, en attente #891
    sys.stdout.write("collect_clicked_notifs: pending #891\n")
    return []


def deduplicate(last_seen):
    return {tup[0]: tup for tup in sorted(last_seen, key=lambda tup: (tup[0], tup[1]))}


def remove_known_last_seen(dedup_last_seen_dict):
    known_last_seen = EmailLastSeen.objects.values_list("email", flat=True)
    return {k: v for k, v in dedup_last_seen_dict.items() if k not in known_last_seen}


def insert_last_seen(dedup_last_seen_dict):
    obj = [EmailLastSeen(email=k, last_seen_at=v[1], last_seen_kind=v[2]) for k, v in dedup_last_seen_dict.items()]
    return EmailLastSeen.objects.bulk_create(obj, batch_size=1000)


class Command(BaseCommand):
    help = "hydratation de la table EmailLastSeen avec la date de dernière visite des emails connus"

    def handle(self, *args, **options):
        last_seen = collect_users_logged_in()
        sys.stdout.write(f"users logged in: collected {len(last_seen)}\n")

        last_seen += collect_event()
        sys.stdout.write(f"events: collected {len(last_seen)}\n")

        last_seen += collect_DSP()
        sys.stdout.write(f"DSP: collected {len(last_seen)}\n")

        last_seen += collect_upvote()
        sys.stdout.write(f"UpVotes: collected {len(last_seen)}\n")

        last_seen += collect_forum_rating()
        sys.stdout.write(f"forum ratings: collected {len(last_seen)}\n")

        last_seen += collect_post()
        sys.stdout.write(f"posts: collected {len(last_seen)}\n")

        last_seen += collect_clicked_notifs()
        sys.stdout.write(f"clicked notifications: collected {len(last_seen)}\n")

        dedup_last_seen_dict = deduplicate(last_seen)
        sys.stdout.write(f"deduplication: {len(dedup_last_seen_dict)}\n")

        dedup_last_seen_dict = remove_known_last_seen(dedup_last_seen_dict)
        sys.stdout.write(f"remove known last seen: {len(dedup_last_seen_dict)}\n")

        res = insert_last_seen(dedup_last_seen_dict)
        sys.stdout.write(f"insert last seen: {len(res)}\n")

        sys.stdout.write("that's all folks!\n")
        sys.stdout.flush()
