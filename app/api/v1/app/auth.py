# FastAPI Imports
from fastapi import APIRouter, Depends

# SQLAlchemy Imports
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.api.deps import get_current_da
from app.db.session import get_db
from app.models.user import RdlUserList
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.schemas.response import APIResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate a DA and issue an access/refresh token pair."""
    tokens = await auth_service.login(db, payload.da_code, payload.password, payload.force)
    return APIResponse(message="Login successful", data=tokens)


@router.post("/refresh", response_model=APIResponse[RefreshResponse])
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Issue a new access token from a valid refresh token."""
    access_token = await auth_service.refresh(db, payload.refresh_token)
    return APIResponse(message="Token refreshed", data=RefreshResponse(access_token=access_token))


@router.post("/logout", response_model=APIResponse)
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke the given refresh token. Always reports success."""
    await auth_service.logout(db, payload.refresh_token)
    return APIResponse(message="Logged out successfully")


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Change the authenticated DA's password and end all sessions."""
    await auth_service.change_password(
        db, current_da.da_code, payload.old_password, payload.new_password
    )
    return APIResponse(message="Password changed successfully")


@router.get("/me", response_model=APIResponse[dict])
async def get_me(current_da: RdlUserList = Depends(get_current_da)):
    """Return the authenticated DA's profile."""
    return APIResponse(
        message="Current user data",
        data={
            "da_code": current_da.da_code,
            "da_name": current_da.da_name,
            "depot_code": current_da.depot_code,
        },
    )