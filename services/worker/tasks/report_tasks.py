from celery import shared_task


@shared_task
def generate_report(tenant_id: str, date: str):
    return {"status": "generated", "tenant_id": tenant_id}
