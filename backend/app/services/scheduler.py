"""Scheduler service for automated bill synchronization.

This module provides scheduled task execution using APScheduler.
"""

import logging
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


async def scheduled_sync() -> None:
    """Execute scheduled bill synchronization.

    This function is called automatically on the 16th of each month at 2:00 AM.
    It syncs bills from all configured email accounts.
    """
    logger.info("Starting scheduled bill sync task")

    try:
        from app.services.sync_service import SyncService

        service = SyncService()
        await service.run_sync()

        logger.info(
            f"Scheduled sync completed: "
            f"processed={service.processed_count}, "
            f"skipped={service.skipped_count}, "
            f"errors={service.error_count}"
        )
    except Exception as e:
        logger.error(f"Scheduled sync failed: {e}")


def init_scheduler() -> None:
    """Initialize and start the scheduler.

    Adds a job that runs on the 16th of each month at 2:00 AM (Asia/Shanghai).
    """
    scheduler.add_job(
        scheduled_sync,
        CronTrigger(day=16, hour=2, minute=0),
        id="monthly_bill_sync",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started: monthly bill sync scheduled for 16th at 02:00 (Asia/Shanghai)")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown complete")
