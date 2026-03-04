from fastapi import APIRouter, Depends

router = APIRouter()


@router.post("/process")
async def process_with_agent(data: dict, tenant_id: str = Depends(lambda: "default")):
    return {"status": "processed", "agent": "orchestrator"}
