from django.db import models
from core.models import BaseTenantModel
from children.models import Child

PRESENCE = (("present", "Present"), ("absent", "Absent"))
STATUS = (("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"))

class AttendanceRecord(BaseTenantModel):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=PRESENCE, default="present")
    time = models.CharField(max_length=8, blank=True, default="")  # e.g. "09:15"

class ExtraHourRequest(BaseTenantModel):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="extra_hours")
    start = models.TimeField()
    end = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
