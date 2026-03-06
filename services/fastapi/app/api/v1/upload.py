from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

router = APIRouter()


@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls files accepted")
    return {"upload_id": "placeholder", "status": "processing", "filename": file.filename}


@router.post("/photo")
async def upload_photo(
    file: UploadFile = File(...),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files accepted")
    return {"upload_id": "placeholder", "status": "processing", "filename": file.filename}
