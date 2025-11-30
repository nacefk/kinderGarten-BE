# Generated migration for chat app - add tenant field and unique constraints
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
        ("chat", "0001_initial"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        # Add tenant field to Conversation
        migrations.AddField(
            model_name="conversation",
            name="tenant",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
            ),
            preserve_default=False,
        ),
        # Add tenant field to Message
        migrations.AddField(
            model_name="message",
            name="tenant",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="core.tenant"
            ),
            preserve_default=False,
        ),
        # Add indexes
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(
                fields=["tenant", "parent"], name="conversation_tenant_parent_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="conversation",
            index=models.Index(
                fields=["tenant", "admin"], name="conversation_tenant_admin_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(
                fields=["conversation", "-created_at"],
                name="message_conversation_date_idx",
            ),
        ),
        # Add unique constraint to prevent duplicate conversations
        migrations.AlterUniqueTogether(
            name="conversation",
            unique_together={("tenant", "parent", "admin")},
        ),
    ]
