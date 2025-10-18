from django.db import models
from core.models import BaseTenantModel
from children.models import Child

class DailyReport(BaseTenantModel):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="reports")
    date = models.DateField()
    meal = models.CharField(max_length=200, blank=True, default="")
    nap = models.CharField(max_length=120, blank=True, default="")
    activity = models.CharField(max_length=200, blank=True, default="")
    behavior = models.CharField(max_length=80, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    submitted_by = models.CharField(max_length=120, blank=True, default="")
