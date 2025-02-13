import hashlib

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from lacommunaute.forum_conversation.models import Post
from lacommunaute.users.models import EmailLastSeen, User


@transaction.atomic
def soft_delete_users(email_last_seen_list):
    emails = [email_last_seen.email for email_last_seen in email_last_seen_list]

    users = list(User.objects.filter(email__in=emails))
    posts = list(Post.objects.filter(username__in=emails))

    anonymized_emails = {}

    for email_last_seen in email_last_seen_list:
        email_last_seen.deleted_at = timezone.now()
        salted_email = f"{email_last_seen.email}-{settings.EMAIL_LAST_SEEN_HASH_SALT}"
        email_last_seen.email_hash = hashlib.sha256(salted_email.encode("utf-8")).hexdigest()
        anonymized_emails[email_last_seen.email] = f"email-anonymise-{email_last_seen.id}@{settings.COMMU_FQDN}"
        email_last_seen.email = anonymized_emails[email_last_seen.email]

    for user in users:
        user.email = anonymized_emails[user.email]
        user.first_name = "Anonyme"
        user.last_name = "Anonyme"

    for post in posts:
        post.username = anonymized_emails[post.username]

    user_count = User.objects.bulk_update(users, ["email", "first_name", "last_name"])
    post_count = Post.objects.bulk_update(posts, ["username"])
    email_last_seen_count = EmailLastSeen.objects.bulk_update(
        email_last_seen_list,
        ["email", "email_hash", "deleted_at"],
    )

    return user_count, post_count, email_last_seen_count
