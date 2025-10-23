from celery import shared_task
from zoneinfo import ZoneInfo
from django.utils import timezone
from .models import DailyReport

@shared_task
def clear_daily_reports():
    """
    Deletes all daily reports automatically every midnight (Tunis time).
    """
    tz = ZoneInfo("Africa/Tunis")
    now = timezone.now().astimezone(tz)
    print(f"🕛 Running clear_daily_reports at {now}")

    DailyReport.objects.all().delete()
    print("✅ All daily reports cleared successfully.")
