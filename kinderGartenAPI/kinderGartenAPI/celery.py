import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinderGartenAPI.settings")

app = Celery("kinderGartenAPI")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "cleanup-daily-reports-every-midnight": {
        "task": "reports.tasks.clear_daily_reports",  # 👈 FIXED name
        "schedule": crontab(hour=0, minute=0),
    },
}
