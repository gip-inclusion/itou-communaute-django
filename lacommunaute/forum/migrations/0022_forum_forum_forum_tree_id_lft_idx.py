from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0021_remove_forum_kind"),
        ("forum_conversation", "0009_run_management"),
        ("partner", "0002_alter_partner_options"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
    ]

    operations = [
        migrations.RunSQL("DROP INDEX IF EXISTS forum_forum_tree_id_lft_idx;", elidable=True),
        migrations.AddIndex(
            model_name="forum",
            index=models.Index(fields=["tree_id", "lft"], name="forum_forum_tree_id_lft_idx"),
        ),
    ]
