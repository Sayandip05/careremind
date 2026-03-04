from fastapi import APIRouter, Depends
from app.schemas.patient import PatientResponse
from typing import List

router = APIRouter()


@router.get("/", response_model=List[PatientResponse])
async def list_patients(tenant_id: str = Depends(lambda: "default")):
    return []


@router.post("/")
async def create_patient(tenant_id: str = Depends(lambda: "default")):
    return {"id": "placeholder"}
