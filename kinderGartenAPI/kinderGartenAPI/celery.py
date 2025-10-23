import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinderGartenAPI.settings")

app = Celery("kinderGartenAPI")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
