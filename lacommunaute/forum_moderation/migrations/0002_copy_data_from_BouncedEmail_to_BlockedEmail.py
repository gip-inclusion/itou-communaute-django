from django.db import migrations


def copy_emails(apps, schema_editor):
    BouncedEmail = apps.get_model("notification", "BouncedEmail")
    BlockedEmail = apps.get_model("forum_moderation", "BlockedEmail")

    for bounced_email in BouncedEmail.objects.all():
        BlockedEmail.objects.create(
            email=bounced_email.email,
            reason=bounced_email.reason,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0007_bounceddomainname"),
        ("forum_moderation", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(copy_emails),
    ]
