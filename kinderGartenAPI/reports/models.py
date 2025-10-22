from django.db import models
from core.models import BaseTenantModel
from children.models import Child
from django.utils import timezone


class DailyReport(BaseTenantModel):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Enfant",
    )
    date = models.DateField(default=timezone.now, verbose_name="Date du rapport")

    meal = models.CharField(max_length=200, blank=True, default="", verbose_name="Repas")
    nap = models.CharField(max_length=120, blank=True, default="", verbose_name="Sieste")
    behavior = models.CharField(max_length=80, blank=True, default="", verbose_name="Comportement")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    submitted_by = models.CharField(max_length=120, blank=True, default="", verbose_name="Soumis par")

    class Meta:
        verbose_name = "Rapport journalier"
        verbose_name_plural = "Rapports journaliers"
        ordering = ["-date"]
        unique_together = ("tenant", "child", "date")  # ✅ Prevent duplicate daily reports per child

    def __str__(self):
        return f"{self.child.name} - {self.date.strftime('%Y-%m-%d')}"
