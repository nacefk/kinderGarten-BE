from django.db import models
from core.models import BaseTenantModel
from children.models import Child


def report_media_path(instance, filename):
    # Organize uploads like: media/reports/child_<id>/<filename>
    return f"reports/child_{instance.report.child.id}/{filename}"


class DailyReport(BaseTenantModel):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name="Enfant",
    )
    meal = models.CharField(max_length=200, blank=True, default="", verbose_name="Repas")
    nap = models.CharField(max_length=120, blank=True, default="", verbose_name="Sieste")
    behavior = models.CharField(max_length=80, blank=True, default="", verbose_name="Comportement")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")

    has_mobile_app = models.BooleanField(default=False)
    submitted_by = models.CharField(max_length=120, blank=True, default="", verbose_name="Soumis par")

    class Meta:
        verbose_name = "Rapport journalier"
        verbose_name_plural = "Rapports journaliers"

    def __str__(self):
        return f"Rapport de {self.child.name}"


class ReportMedia(BaseTenantModel):
    """Store multiple photos/videos per daily report"""

    report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name="media_files",
        verbose_name="Rapport associé",
    )
    file = models.FileField(
        upload_to=report_media_path,
        verbose_name="Photo/Vidéo",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fichier média du rapport"
        verbose_name_plural = "Fichiers médias des rapports"

    def __str__(self):
        return f"Média du rapport {self.report_id}"
