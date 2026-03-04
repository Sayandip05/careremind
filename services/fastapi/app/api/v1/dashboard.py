from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(tenant_id: str = Depends(lambda: "default")):
    return {
        "total_patients": 0,
        "pending_reminders": 0,
        "sent_today": 0,
        "success_rate": 0,
    }
