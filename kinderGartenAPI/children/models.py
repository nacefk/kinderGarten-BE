from django.db import models
from core.models import BaseTenantModel
from datetime import date


class ClassRoom(BaseTenantModel):
    name = models.CharField(max_length=80)
    teacher_name = models.CharField(max_length=120, blank=True, default="")
    assistant_name = models.CharField(max_length=120, blank=True, default="")
    age_range = models.CharField(max_length=40, blank=True, default="")
    room = models.CharField(max_length=40, blank=True, default="")
    students_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Club(BaseTenantModel):
    """Represents an extracurricular or in-class club (music, sport, etc.)"""

    name = models.CharField(max_length=120, verbose_name="Nom du club")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    instructor_name = models.CharField(max_length=120, blank=True, default="", verbose_name="Encadrant")
    schedule = models.CharField(max_length=120, blank=True, default="", verbose_name="Horaires")

    def __str__(self):
        return self.name
class Child(BaseTenantModel):
    name = models.CharField(max_length=120)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, default="")
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.SET_NULL, null=True, related_name="children"
    )
    parent_name = models.CharField(max_length=120)
    avatar = models.CharField(max_length=500, blank=True, default="")
    clubs = models.ManyToManyField(
        "Club",
        related_name="children",
        blank=True,
        verbose_name="Clubs",
    )
    allergies = models.TextField(blank=True, default="")
    conditions = models.TextField(blank=True, default="")
    medication = models.TextField(blank=True, default="")
    doctor = models.CharField(max_length=120, blank=True, default="")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    emergency_contact_name = models.CharField(max_length=120, blank=True, default="")
    emergency_contact_relation = models.CharField(max_length=120, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=40, blank=True, default="")
    responsible_name = models.CharField(max_length=120, blank=True, default="")
    responsible_phone = models.CharField(max_length=40, blank=True, default="")


    next_payment_date = models.DateField(null=True, blank=True)

    # ✅ New field
    has_mobile_app = models.BooleanField(default=False)

    def __str__(self):
        return self.name
