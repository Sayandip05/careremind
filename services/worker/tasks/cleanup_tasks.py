from celery import shared_task


@shared_task
def cleanup_old_files():
    return {"status": "cleaned"}
