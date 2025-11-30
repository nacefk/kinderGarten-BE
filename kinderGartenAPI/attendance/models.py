from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from core.models import BaseTenantModel
from children.models import Child


class AttendanceStatus(models.TextChoices):
    """Attendance record status"""

    PRESENT = "present", "Present"
    ABSENT = "absent", "Absent"


class ExtraHourStatus(models.TextChoices):
    """Extra hour request status"""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class AttendanceRecord(BaseTenantModel):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="attendance",
        db_index=True,
    )
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.PRESENT,
    )

    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        unique_together = [["tenant", "child", "date"]]  # One record per child per day
        indexes = [
            models.Index(fields=["tenant", "date"]),
            models.Index(fields=["tenant", "child", "date"]),
        ]

    def clean(self):
        """Validate before save"""
        if self.date > timezone.now().date():
            raise ValidationError("Cannot record attendance for future dates")

    def __str__(self):
        return f"{self.child.name} - {self.date} ({self.status})"


class ExtraHourRequest(BaseTenantModel):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="extra_hours",
        db_index=True,
    )
    start = models.TimeField()
    end = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=ExtraHourStatus.choices,
        default=ExtraHourStatus.PENDING,
    )

    class Meta:
        verbose_name = "Extra Hour Request"
        verbose_name_plural = "Extra Hour Requests"
        indexes = [
            models.Index(fields=["tenant", "child"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.child.name} - {self.start} to {self.end} ({self.status})"
