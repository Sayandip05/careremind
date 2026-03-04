from celery import shared_task


@shared_task
def process_excel(file_id: str):
    return {"status": "processed", "file_id": file_id}
