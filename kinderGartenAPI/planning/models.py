from django.db import models
from core.models import BaseTenantModel
from children.models import ClassRoom

class Event(BaseTenantModel):
    title = models.CharField(max_length=160)
    date = models.DateTimeField()
    description = models.TextField(blank=True, default="")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)

class PlanActivity(BaseTenantModel):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="plan")
    day = models.CharField(max_length=12)  # "Lundi"..."Vendredi"
    time = models.CharField(max_length=8)  # "08:00"
    title = models.CharField(max_length=160)
