from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseTenantModel

User = get_user_model()


class Conversation(BaseTenantModel):
    parent = models.ForeignKey(
        User,
        related_name="parent_conversations",
        on_delete=models.CASCADE,
        db_index=True,
    )
    admin = models.ForeignKey(
        User,
        related_name="admin_conversations",
        on_delete=models.CASCADE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        unique_together = [["tenant", "parent", "admin"]]
        indexes = [
            models.Index(fields=["tenant", "parent"]),
            models.Index(fields=["tenant", "admin"]),
        ]

    def __str__(self):
        return f"{self.parent.username} ↔ {self.admin.username}"


class Message(BaseTenantModel):
    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
        db_index=True,
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ["timestamp"]
        indexes = [
            models.Index(fields=["tenant", "conversation"]),
            models.Index(fields=["tenant", "timestamp"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self):
        return f"{self.sender.username}: {self.text[:25]}"
