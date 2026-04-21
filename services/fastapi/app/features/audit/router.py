import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
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
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(50, ge=1, le=200, description="Records per page"),
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated audit logs for the authenticated tenant.
    """
    try:
        base_stmt = select(AuditLog).where(AuditLog.tenant_id == tenant.id)

        if resource:
            base_stmt = base_stmt.where(AuditLog.resource == resource)
        if resource_id:
            base_stmt = base_stmt.where(AuditLog.resource_id == resource_id)

        # Count total records for pagination metadata
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # Fetch paginated records
        offset = (page - 1) * per_page
        stmt = (
            base_stmt
            .order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await db.execute(stmt)
        logs = result.scalars().all()

        return {
            "data": logs,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
            },
        }
    except Exception as e:
        logger.error("Failed to fetch audit logs: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")

