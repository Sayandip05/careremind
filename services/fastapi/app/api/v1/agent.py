from fastapi import APIRouter

router = APIRouter()


@router.post("/process")
async def process_with_agent(data: dict):
    return {"status": "processed", "agent": "orchestrator"}
