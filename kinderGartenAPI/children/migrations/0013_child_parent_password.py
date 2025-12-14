# Generated migration for parent_password field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("children", "0012_child_parent_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="child",
            name="parent_password",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Encrypted password for parent user account",
                max_length=255,
                verbose_name="Parent account password",
            ),
        ),
    ]
