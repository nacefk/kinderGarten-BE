# Generated migration for reports app - add indexes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        # Add indexes for performance
        migrations.AddIndex(
            model_name="dailyreport",
            index=models.Index(
                fields=["tenant", "child"], name="report_tenant_child_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="dailyreport",
            index=models.Index(
                fields=["tenant", "date"], name="report_tenant_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="dailyreport",
            index=models.Index(
                fields=["tenant", "child", "date"], name="report_tenant_child_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="reportmedia",
            index=models.Index(
                fields=["report", "media_type"], name="reportmedia_report_type_idx"
            ),
        ),
    ]
