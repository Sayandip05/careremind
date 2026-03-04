from celery import shared_task


@shared_task
def send_reminder(reminder_id: str):
    return {"status": "sent", "reminder_id": reminder_id}
