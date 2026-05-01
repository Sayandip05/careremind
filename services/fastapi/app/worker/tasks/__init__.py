"""
Background task registry.

All tasks are auto-discovered by Celery via:
    celery_app.autodiscover_tasks(["app.worker.tasks"])

Task names follow the pattern: app.worker.tasks.<module>.<function>
"""

from app.worker.tasks.reminder_tasks import (  # noqa: F401
    send_pending_reminders,
    send_single_reminder,
    retry_failed_reminders,
)
from app.worker.tasks.excel_tasks import process_excel_upload  # noqa: F401
from app.worker.tasks.ocr_tasks import process_photo_upload  # noqa: F401
from app.worker.tasks.report_tasks import generate_daily_summary  # noqa: F401
from app.worker.tasks.cleanup_tasks import (  # noqa: F401
    cleanup_old_uploads,
    cleanup_expired_reminders,
)
