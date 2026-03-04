from celery import shared_task


@shared_task
def process_ocr(image_id: str):
    return {"status": "processed", "image_id": image_id}
