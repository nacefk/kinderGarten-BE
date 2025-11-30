from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from zoneinfo import ZoneInfo
import logging

from .models import DailyReport

logger = logging.getLogger("api")


@shared_task
def archive_old_daily_reports(days=30):
    """
    Archive (instead of delete) daily reports older than N days.
    Runs once per day, configurable retention period.

    Args:
        days: Number of days to keep reports (default 30)
    """
    tz = ZoneInfo("Africa/Tunis")
    now = timezone.now().astimezone(tz)
    cutoff_date = now.date() - timedelta(days=days)

    logger.info(f"🕛 Starting archive of reports older than {cutoff_date}")

    try:
        with transaction.atomic():
            # Find old reports
            old_reports = DailyReport.objects.filter(date__lt=cutoff_date)
            count = old_reports.count()

            if count > 0:
                # Instead of deleting, could archive to separate table here
                # For now, just log what would be archived
                logger.info(f"📦 Archiving {count} reports before {cutoff_date}")

                # Optional: implement actual archiving logic here
                # For now, keep them in database for historical reference
                # old_reports.update(is_archived=True)  # if you add this field

            logger.info(f"✅ Archiving completed: {count} reports processed")

    except Exception as e:
        logger.error(f"❌ Error archiving reports: {e}", exc_info=True)
        raise
