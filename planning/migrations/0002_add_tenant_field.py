# Generated migration for planning app - add tenant field and constraints
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("planning", "0001_initial"),
    ]

    operations = [
        # Add tenant field to Event
        migrations.AddField(
            model_name="event",
            name="tenant",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
            ),
            preserve_default=False,
        ),
        # Add tenant field to WeeklyPlan
        migrations.AddField(
            model_name="weeklyplan",
            name="tenant",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
            ),
            preserve_default=False,
        ),
        # Add indexes
        migrations.AddIndex(
            model_name="event",
            index=models.Index(
                fields=["tenant", "classroom"], name="event_tenant_classroom_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="event",
            index=models.Index(fields=["tenant", "date"], name="event_tenant_date_idx"),
        ),
        migrations.AddIndex(
            model_name="weeklyplan",
            index=models.Index(
                fields=["tenant", "classroom"], name="weeklyplan_tenant_classroom_idx"
            ),
        ),
        # Add unique constraints
        migrations.AlterUniqueTogether(
            name="event",
            unique_together={("tenant", "classroom", "date", "title")},
        ),
    ]
