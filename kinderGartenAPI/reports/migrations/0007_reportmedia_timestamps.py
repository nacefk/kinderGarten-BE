# Migration to add timestamps to ReportMedia

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0006_remove_dailyreport_media_reportmedia"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportmedia",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="reportmedia",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
