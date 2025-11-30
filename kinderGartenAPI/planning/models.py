from django.db import models
from core.models import BaseTenantModel


class Event(BaseTenantModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    classroom = models.ForeignKey(
        "children.ClassRoom",
        on_delete=models.CASCADE,
        related_name="events",
        db_index=True,
    )

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = [
            models.Index(fields=["tenant", "date"]),
            models.Index(fields=["classroom"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.date})"


class WeeklyPlan(BaseTenantModel):
    classroom = models.ForeignKey(
        "children.ClassRoom",
        on_delete=models.CASCADE,
        related_name="plans",
        db_index=True,
    )
    day = models.CharField(max_length=20)
    time = models.CharField(max_length=10)
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Weekly Plan"
        verbose_name_plural = "Weekly Plans"
        indexes = [
            models.Index(fields=["tenant", "day", "time"]),
            models.Index(fields=["classroom"]),
        ]

    def __str__(self):
        return f"{self.classroom.name} - {self.day} {self.time}"
