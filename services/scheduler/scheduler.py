from apscheduler.schedulers.blocking import BlockingScheduler
from jobs.daily_reminder_job import run_daily_reminder
from jobs.summary_report_job import run_summary_report
from jobs.retry_failed_job import run_retry_failed
from jobs.cleanup_job import run_cleanup

scheduler = BlockingScheduler()

scheduler.add_job(run_daily_reminder, "cron", hour=9, minute=0)
scheduler.add_job(run_summary_report, "cron", hour=9, minute=30)
scheduler.add_job(run_retry_failed, "cron", hour=11, minute=0)
scheduler.add_job(run_cleanup, "cron", hour=0, minute=0)

if __name__ == "__main__":
    scheduler.start()
