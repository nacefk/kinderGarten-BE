# Generated migration for children app - add indexes and constraints
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("children", "0012_child_parent_user"),
    ]

    operations = [
        # Add indexes for performance optimization
        migrations.AddIndex(
            model_name="child",
            index=models.Index(
                fields=["tenant", "classroom"], name="child_tenant_classroom_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="child",
            index=models.Index(
                fields=["tenant", "parent_user"], name="child_tenant_parent_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="child",
            index=models.Index(
                fields=["tenant", "-created_at"], name="child_tenant_created_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="classroom",
            index=models.Index(
                fields=["tenant", "name"], name="classroom_tenant_name_idx"
            ),
        ),
    ]
