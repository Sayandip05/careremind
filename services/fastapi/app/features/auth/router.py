"""
Auth routes — registration, login, and tenant profile.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_tenant
from app.features.auth.models import Tenant
from app.features.auth.schemas import TenantResponse, TenantUpdate, TenantRegister, TokenResponse
from app.features.auth import service as auth_service
from app.specialty import list_known_specialties

router = APIRouter()


@router.get("/specialties", response_model=list[str])
async def get_specialties():
    """
    Public endpoint — returns all known specialty names for frontend dropdowns.
    The last item is always 'Other' to enable free-text input.
    """
    return list_known_specialties()


from fastapi import Request
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from app.core.config import settings

google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/api/v1/auth/callback/google",
    allow_insecure_http=True,
)

facebook_sso = FacebookSSO(
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    redirect_uri="http://localhost:8000/api/v1/auth/callback/facebook",
    allow_insecure_http=True,
)

@router.get("/login/google")
async def google_login():
    """Redirects to Google Auth portal"""
    with google_sso:
        return await google_sso.get_login_redirect()

@router.get("/callback/google", response_model=TokenResponse)
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles Google Auth callback and returns JWT"""
    with google_sso:
        openid = await google_sso.verify_and_process(request)
    return await auth_service.authenticate_sso(openid, db)


@router.get("/login/facebook")
async def facebook_login():
    """Redirects to Facebook Auth portal"""
    with facebook_sso:
        return await facebook_sso.get_login_redirect()

@router.get("/callback/facebook", response_model=TokenResponse)
async def facebook_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles Facebook Auth callback and returns JWT"""
    with facebook_sso:
        openid = await facebook_sso.verify_and_process(request)
    return await auth_service.authenticate_sso(openid, db)


@router.post("/register", response_model=TenantResponse)
async def register(
    data: TenantRegister,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new doctor account.
    Consolidates functionality.
    """
    tenant = await auth_service.register_tenant(data, db)
    return tenant


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
    return await auth_service.authenticate_tenant(form_data.username, form_data.password, db)



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
