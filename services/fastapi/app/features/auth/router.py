"""
Auth routes — registration, login, and tenant profile.
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.auth.models import Tenant
from app.features.auth.schemas import TenantResponse, TenantUpdate, TenantRegister, TokenResponse
from app.features.auth import service as auth_service
from app.specialty import list_known_specialties

logger = logging.getLogger("careremind.auth")

router = APIRouter()


@router.get("/specialties", response_model=list[str])
async def get_specialties():
    """
    Public endpoint — returns all known specialty names for frontend dropdowns.
    The last item is always 'Other' to enable free-text input.
    """
    return list_known_specialties()


from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from app.core.config import settings

google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri=f"{settings.API_BASE_URL}/api/v1/auth/callback/google",
    allow_insecure_http=not settings.is_production,
)

facebook_sso = FacebookSSO(
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    redirect_uri=f"{settings.API_BASE_URL}/api/v1/auth/callback/facebook",
    allow_insecure_http=not settings.is_production,
)

@router.get("/login/google")
async def google_login():
    """Redirects to Google Auth portal"""
    with google_sso:
        return await google_sso.get_login_redirect()

@router.get("/callback/google")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles Google Auth callback — redirects to frontend with JWT token."""
    try:
        with google_sso:
            openid = await google_sso.verify_and_process(request)
        
        if not openid or not openid.email:
            logger.warning("Google OAuth failed: email not provided")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=Email+not+provided+by+Google"
            )
        
        result = await auth_service.authenticate_sso(openid, db)
        logger.info(
            "Google OAuth successful: email=%s, tenant_id=%s, doctor_name=%s",
            openid.email,
            result.tenant_id,
            result.doctor_name
        )
        # Redirect to frontend with token in URL — frontend will extract and store it
        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}/login"
                f"?token={result.access_token}"
                f"&tenant_id={result.tenant_id}"
                f"&doctor_name={result.doctor_name}"
            )
        )
    except Exception as e:
        logger.error("Google OAuth error: %s", str(e), exc_info=True)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=OAuth+failed"
        )


@router.get("/login/facebook")
async def facebook_login():
    """Redirects to Facebook Auth portal"""
    with facebook_sso:
        return await facebook_sso.get_login_redirect()

@router.get("/callback/facebook")
async def facebook_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles Facebook Auth callback — redirects to frontend with JWT token."""
    try:
        with facebook_sso:
            openid = await facebook_sso.verify_and_process(request)
        
        if not openid or not openid.email:
            logger.warning("Facebook OAuth failed: email not provided")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/login?error=Email+not+provided+by+Facebook"
            )
        
        result = await auth_service.authenticate_sso(openid, db)
        logger.info(
            "Facebook OAuth successful: email=%s, tenant_id=%s, doctor_name=%s",
            openid.email,
            result.tenant_id,
            result.doctor_name
        )
        return RedirectResponse(
            url=(
                f"{settings.FRONTEND_URL}/login"
                f"?token={result.access_token}"
                f"&tenant_id={result.tenant_id}"
                f"&doctor_name={result.doctor_name}"
            )
        )
    except Exception as e:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=OAuth+failed"
        )


from fastapi import status as http_status

@router.post("/register", response_model=TokenResponse, status_code=http_status.HTTP_201_CREATED)
async def register(
    data: TenantRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new doctor account and return JWT token.
    Consolidates functionality.
    """
    tenant = await auth_service.register_tenant(data, db)
    logger.info(
        "New registration: email=%s, doctor_name=%s, specialty=%s, clinic=%s",
        tenant.email,
        tenant.doctor_name,
        tenant.specialty,
        tenant.clinic_name
    )
    
    # Generate token for immediate login
    from app.core.security import create_access_token
    token = create_access_token(tenant_id=tenant.id, email=tenant.email)
    
    return TokenResponse(
        access_token=token,
        tenant_id=tenant.id,
        doctor_name=tenant.doctor_name,
        clinic_name=tenant.clinic_name,
        email=tenant.email,
        specialty=tenant.specialty,
        plan=tenant.plan.value if tenant.plan else "free",
    )


from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a doctor and return a JWT.
    Consolidates functionality.
    """
    try:
        result = await auth_service.authenticate_tenant(form_data.username, form_data.password, db)
        logger.info("Login successful: email=%s, tenant_id=%s", form_data.username, result.tenant_id)
        return result
    except Exception as e:
        logger.warning("Login failed: email=%s, reason=%s", form_data.username, str(e))
        raise



@router.get("/me", response_model=TenantResponse)
async def get_my_profile(
    tenant: Tenant = Depends(get_current_tenant),
):
    """
    Returns the authenticated doctor's profile.
    Validates that the JWT is valid and the account is active.
    """
    return tenant


@router.patch("/me", response_model=TenantResponse)
async def update_my_profile(
    data: TenantUpdate,
    tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Update the authenticated doctor's profile."""
    updated = await auth_service.update_profile(tenant, data, db)
    return updated
