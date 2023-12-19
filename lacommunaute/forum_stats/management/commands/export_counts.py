import csv

from django.core.management.base import BaseCommand
from django.db.models import Count, F, Max, Min

from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.users.models import User


def export_users():
    qs = User.objects.values("email", "date_joined", "last_login").order_by("email")
    with open("exports/users.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "oldest", "most_recent"])
        for user in qs:
            writer.writerow([user["email"], user["date_joined"], user["last_login"]])


def export_upvotes():
    qs = User.objects.values("email").order_by("email").annotate(upvotes=Count("upvotes"))
    with open("exports/upvotes.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "upvotes"])
        for user in qs:
            writer.writerow([user["email"], user["upvotes"]])


def export_authenticated_users_topics():
    qs = (
        Topic.objects.exclude(poster__isnull=True)
        .values(email=F("poster__email"))
        .order_by("poster__email")
        .annotate(topics=Count("id"), oldest=Min("created"), most_recent=Max("created"))
    )
    with open("exports/authenticated_users_topics.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "topics", "oldest", "most_recent"])
        for q in qs:
            writer.writerow([q["email"], q["topics"], q["oldest"], q["most_recent"]])


def export_authenticated_users_posts():
    qs = (
        Post.objects.exclude(poster__isnull=True)
        .values(email=F("poster__email"))
        .order_by("poster__email")
        .annotate(posts=Count("id"), oldest=Min("created"), most_recent=Max("created"))
    )
    with open("exports/authenticated_users_posts.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "posts", "oldest", "most_recent"])
        for q in qs:
            writer.writerow([q["email"], q["posts"], q["oldest"], q["most_recent"]])


def export_anonymous_users_topics():
    qs = (
        Topic.objects.filter(poster__isnull=True)
        .values(email=F("first_post__username"))
        .order_by("first_post__username")
        .annotate(topics=Count("id"), oldest=Min("created"), most_recent=Max("created"))
    )
    with open("exports/anonymous_users_topics.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "topics", "oldest", "most_recent"])
        for q in qs:
            writer.writerow([q["email"], q["topics"], q["oldest"], q["most_recent"]])


def export_anonymous_users_posts():
    qs = (
        Post.objects.filter(poster__isnull=True)
        .values(email=F("username"))
        .order_by("username")
        .annotate(posts=Count("username"), oldest=Min("created"), most_recent=Max("created"))
    )
    with open("exports/anonymous_users_posts.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["email", "posts", "oldest", "most_recent"])
        for q in qs:
            writer.writerow([q["email"], q["posts"], q["oldest"], q["most_recent"]])


class Command(BaseCommand):
    help = "Export activities stats"

    def handle(self, **options):
        print("Exporting users...")
        export_users()

        print("Exporting upvotes...")
        export_upvotes()

        print("Exporting authenticated users topics...")
        export_authenticated_users_topics()

        print("Exporting authenticated users posts...")
        export_authenticated_users_posts()

        print("Exporting anonymous users topics...")
        export_anonymous_users_topics()

        print("Exporting anonymous users posts...")
        export_anonymous_users_posts()
