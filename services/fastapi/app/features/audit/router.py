import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.audit.models import AuditLog
from app.features.auth.models import Tenant

logger = logging.getLogger("careremind.audit")

router = APIRouter()


@router.get("/")
async def get_audit_logs(
    resource: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit logs for the authenticated tenant.
    """
    try:
        stmt = select(AuditLog).where(AuditLog.tenant_id == tenant.id)

        if resource:
            stmt = stmt.where(AuditLog.resource == resource)
        if resource_id:
            stmt = stmt.where(AuditLog.resource_id == resource_id)

        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(100)

        result = await db.execute(stmt)
        logs = result.scalars().all()
        return logs
    except Exception as e:
        logger.error("Failed to fetch audit logs: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")
