from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    class_name = models.ForeignKey(
        "children.ClassRoom", on_delete=models.CASCADE, related_name="events"
    )

    def __str__(self):
        return f"{self.title} ({self.date})"


class WeeklyPlan(models.Model):
    class_name = models.ForeignKey(
        "children.ClassRoom", on_delete=models.CASCADE, related_name="plans"
    )
    day = models.CharField(max_length=20)
    time = models.CharField(max_length=10)
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.class_name.name} - {self.day} {self.time}"
