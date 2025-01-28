from datetime import datetime

from django.core.management import call_command
from django.utils import timezone

from lacommunaute.event.factories import EventFactory
from lacommunaute.forum.factories import ForumFactory, ForumRatingFactory
from lacommunaute.forum_conversation.factories import AnonymousTopicFactory, TopicFactory
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import EmailLastSeenFactory, UserFactory
from lacommunaute.users.management.commands.populate_emaillastseen import (
    collect_DSP,
    collect_event,
    collect_forum_rating,
    collect_post,
    collect_upvote,
    collect_users_logged_in,
    deduplicate,
    insert_last_seen,
    remove_known_last_seen,
)
from lacommunaute.users.models import EmailLastSeen


def test_collect_users_logged_in(db):
    logged_user = UserFactory(last_login=timezone.make_aware(datetime(2024, 10, 22)))
    UserFactory(last_login=None)
    assert collect_users_logged_in() == [(logged_user.email, logged_user.last_login, EmailLastSeenKind.LOGGED)]


def test_collect_event(db):
    event = EventFactory()
    assert collect_event() == [(event.poster.email, event.created, EmailLastSeenKind.EVENT)]


def test_collect_DSP(db):
    dsp = DSPFactory()
    assert collect_DSP() == [(dsp.user.email, dsp.created, "DSP")]


def test_upvote(db):
    upvote = UpVoteFactory(content_object=ForumFactory(), voter=UserFactory())
    assert collect_upvote() == [(upvote.voter.email, upvote.created_at, EmailLastSeenKind.UPVOTE)]


def test_forum_rating(db):
    ForumRatingFactory(user=None)
    forum_rating = ForumRatingFactory(user=UserFactory())
    assert collect_forum_rating() == [(forum_rating.user.email, forum_rating.created, EmailLastSeenKind.FORUM_RATING)]


def test_collect_post(db):
    topic = TopicFactory(with_post=True)
    anonymous_topic = AnonymousTopicFactory(with_post=True)

    assert collect_post() == [
        (topic.first_post.poster.email, topic.first_post.created, EmailLastSeenKind.POST),
        (anonymous_topic.first_post.username, anonymous_topic.first_post.created, EmailLastSeenKind.POST),
    ]


def test_collect_clicked_notifs():
    # TODO VincentPorte, en attente #891
    assert False


def test_deduplicate():
    emails = ["toby@roberts.com", "adam@ondra.com", "jakob@schubert.com"]
    last_seen = [(email, timezone.now(), kind) for email in emails for kind in EmailLastSeenKind.values]

    deduplicated = deduplicate(last_seen)
    for email in list(set(emails)):
        assert deduplicated[email][0] == email
        assert deduplicated[email][2] == EmailLastSeenKind.LOGGED


def test_remove_known_last_seen(db):
    emails = ["oriane@bertone.com", "catherine@destivelle.com"]
    EmailLastSeenFactory(email=emails[1])
    deduplicated = {email: (email, datetime(2024, 10, 22), EmailLastSeenKind.FORUM_RATING) for email in emails}

    output = remove_known_last_seen(deduplicated)
    assert emails[0] in output
    assert emails[1] not in output


def test_insert_last_seen(db):
    emails = ["brooke@raboutou.com", "natalia@grossman.com"]
    kinds = [EmailLastSeenKind.POST, EmailLastSeenKind.LOGGED]
    deduplicated = {email: (email, datetime(2024, 10, 22), kind) for email, kind in zip(emails, kinds)}

    insert_last_seen(deduplicated)
    assert EmailLastSeen.objects.count() == 2
    for email, kind in zip(emails, kinds):
        email_last_seen = EmailLastSeen.objects.get(email=email)
        assert email_last_seen.last_seen_kind == kind


def test_populate_emaillastseen_command(db):
    user = UserFactory(last_login=timezone.make_aware(datetime(2024, 10, 22)))
    event = EventFactory()
    dsp = DSPFactory()
    upvote = UpVoteFactory(content_object=ForumFactory(), voter=UserFactory())
    forum_rating = ForumRatingFactory(user=UserFactory())
    topic = TopicFactory(with_post=True)
    anonymous_topic = AnonymousTopicFactory(with_post=True)
    # TODO VincentPorte, en attente #891
    # clicked_notification = NotificationFactory(visited_at=timezone.now())

    # duplicated email
    event_for_duplicated = EventFactory()
    DSPFactory(user=event_for_duplicated.poster)

    # already known email
    event_for_known = EventFactory()
    EmailLastSeen.objects.all().delete()
    EmailLastSeenFactory(email=event_for_known.poster.email, last_seen_kind=EmailLastSeenKind.FORUM_RATING)

    call_command("populate_emaillastseen")

    assert EmailLastSeen.objects.count() == 9
    assert EmailLastSeen.objects.filter(email=user.email, last_seen_kind=EmailLastSeenKind.LOGGED).exists()
    assert EmailLastSeen.objects.filter(email=event.poster.email, last_seen_kind=EmailLastSeenKind.EVENT).exists()
    assert EmailLastSeen.objects.filter(email=dsp.user.email, last_seen_kind=EmailLastSeenKind.DSP).exists()
    assert EmailLastSeen.objects.filter(email=upvote.voter.email, last_seen_kind=EmailLastSeenKind.UPVOTE).exists()
    assert EmailLastSeen.objects.filter(
        email=forum_rating.user.email, last_seen_kind=EmailLastSeenKind.FORUM_RATING
    ).exists()
    assert EmailLastSeen.objects.filter(
        email=topic.first_post.poster.email, last_seen_kind=EmailLastSeenKind.POST
    ).exists()
    assert EmailLastSeen.objects.filter(
        email=anonymous_topic.first_post.username, last_seen_kind=EmailLastSeenKind.POST
    ).exists()
    # TODO VincentPorte, en attente #891
    # assert EmailLastSeen.objects.filter(email=clicked_notification.recipient, last_seen_kind=XXXX).exists()
    assert EmailLastSeen.objects.filter(
        email=event_for_duplicated.poster.email, last_seen_kind=EmailLastSeenKind.DSP
    ).exists()
    assert EmailLastSeen.objects.filter(
        email=event_for_known.poster.email, last_seen_kind=EmailLastSeenKind.FORUM_RATING
    ).exists()
