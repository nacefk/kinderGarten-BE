# Generated migration for attendance app - add indexes and constraints
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0003_remove_attendancerecord_time"),
    ]

    operations = [
        # Add indexes for performance
        migrations.AddIndex(
            model_name="attendancerecord",
            index=models.Index(
                fields=["tenant", "child", "date"],
                name="attendance_tenant_child_date_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="attendancerecord",
            index=models.Index(
                fields=["tenant", "date"], name="attendance_tenant_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="attendancerecord",
            index=models.Index(
                fields=["tenant", "status"], name="attendance_tenant_status_idx"
            ),
        ),
        # Ensure unique attendance record per child per date
        migrations.AlterUniqueTogether(
            name="attendancerecord",
            unique_together={("tenant", "child", "date")},
        ),
    ]
