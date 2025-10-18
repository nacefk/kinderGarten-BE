from django.db import models
from core.models import BaseTenantModel

class ClassRoom(BaseTenantModel):
    name = models.CharField(max_length=80)
    teacher_name = models.CharField(max_length=120, blank=True, default="")
    assistant_name = models.CharField(max_length=120, blank=True, default="")
    age_range = models.CharField(max_length=40, blank=True, default="")
    room = models.CharField(max_length=40, blank=True, default="")
    students_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Child(BaseTenantModel):
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    classroom = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, related_name="children")
    parent_name = models.CharField(max_length=120)
    avatar = models.URLField(blank=True, default="")

    def __str__(self):
        return self.name
