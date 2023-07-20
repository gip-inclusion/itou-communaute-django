import django.db.models.deletion
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def move_forward_foreign_key_to_generic_foreign_key(apps, schema_editor):
    UpVote = apps.get_model("forum_upvote", "UpVote")
    ContentType = apps.get_model("contenttypes", "ContentType")

    UpVote.objects.filter(post__isnull=True).delete()
    content_type, _ = ContentType.objects.get_or_create(model="post", app_label="forum_conversation")

    for upvote in UpVote.objects.all():
        upvote.content_object = upvote.post
        upvote.object_id = upvote.post_id
        upvote.content_type = content_type
        upvote.save()


def move_back_generic_foreign_key_to_foreign_key(apps, schema_editor):
    UpVote = apps.get_model("forum_upvote", "UpVote")
    Post = apps.get_model("forum_conversation", "Post")

    post_content_type_id = ContentType.objects.get(model="post", app_label="forum_conversation").id
    UpVote.objects.exclude(content_type_id=post_content_type_id).delete()

    for upvote in UpVote.objects.all():
        upvote.post = Post.objects.get(id=upvote.object_id)
        upvote.save()


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("forum_upvote", "0003_delete_certifiedpost"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="upvote",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="upvote",
            name="content_type",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype"
            ),
        ),
        migrations.AddField(
            model_name="upvote",
            name="object_id",
            field=models.PositiveBigIntegerField(null=True),
        ),
        migrations.RunPython(
            move_forward_foreign_key_to_generic_foreign_key,
            move_back_generic_foreign_key_to_foreign_key,
        ),
        migrations.AlterUniqueTogether(
            name="upvote",
            unique_together={("voter", "content_type", "object_id")},
        ),
        migrations.AlterField(
            model_name="upvote",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="upvote",
            name="object_id",
            field=models.PositiveBigIntegerField(),
        ),
        migrations.RemoveField(
            model_name="upvote",
            name="post",
        ),
    ]
