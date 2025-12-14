# Generated migration for OneToOneField change

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("children", "0013_child_parent_password"),
        ("reports", "0007_reportmedia_timestamps"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dailyreport",
            name="child",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="report",
                to="children.child",
                verbose_name="Enfant",
                db_index=True,
            ),
        ),
    ]
