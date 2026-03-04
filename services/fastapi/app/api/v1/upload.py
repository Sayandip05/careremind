from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.schemas.upload import UploadResponse
from app.services.notification_service import NotificationService
from app.agents.orchestrator import Orchestrator

router = APIRouter()


@router.post("/excel", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(...), tenant_id: str = Depends(lambda: "default")
):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files accepted")
    return {"status": "processing", "file_id": "placeholder"}


@router.post("/photo", response_model=UploadResponse)
async def upload_photo(
    file: UploadFile = File(...), tenant_id: str = Depends(lambda: "default")
):
    if not file.filename.endswith((".jpg", ".png")):
        raise HTTPException(status_code=400, detail="Only .jpg and .png files accepted")
    return {"status": "processing", "file_id": "placeholder"}
