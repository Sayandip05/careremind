from fastapi import APIRouter, Depends
from app.schemas.reminder import ReminderResponse
from typing import List

router = APIRouter()


@router.get("/", response_model=List[ReminderResponse])
async def list_reminders(tenant_id: str = Depends(lambda: "default")):
    return []


@router.post("/trigger/{appointment_id}")
async def trigger_reminder(
    appointment_id: str, tenant_id: str = Depends(lambda: "default")
):
    return {"status": "triggered"}
