from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.models.audit_log import AuditLog
from app.models.tenant import Tenant

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
    stmt = select(AuditLog).where(AuditLog.tenant_id == tenant.id)
    
    if resource:
        stmt = stmt.where(AuditLog.resource == resource)
    if resource_id:
        stmt = stmt.where(AuditLog.resource_id == resource_id)
        
    stmt = stmt.order_by(AuditLog.created_at.desc()).limit(100)
    
    result = await db.execute(stmt)
    return result.scalars().all()
