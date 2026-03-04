from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    return JSONResponse(status_code=200, content={"status": "ok"})


@router.post("/razorpay")
async def razorpay_webhook(request: Request):
    return JSONResponse(status_code=200, content={"status": "ok"})
