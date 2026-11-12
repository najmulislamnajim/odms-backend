# Python Imports
from datetime import datetime, timedelta, timezone

# FastAPI Imports
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy Imports
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.api.deps import get_current_da
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    hash_refresh_token,
    create_access_token,
    generate_refresh_token,
)
from app.db.session import get_db
from app.models.refresh_token import RdlRefreshToken
from app.models.user import RdlUserList
from app.models.user_credential import RdlUserCredential
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    ChangePasswordRequest,
)
from app.schemas.response import APIResponse

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_credential(db: AsyncSession, da_code: str) -> RdlUserCredential | None:
    """Fetch the credential row for a given DA code."""
    result = await db.execute(
        select(RdlUserCredential).where(RdlUserCredential.da_code == da_code)
    )
    return result.scalar_one_or_none()


async def _has_active_session(db: AsyncSession, da_code: str) -> bool:
    """Return True if the DA already has a usable (not revoked, not expired) session."""
    result = await db.execute(
        select(RdlRefreshToken.id).where(
            RdlRefreshToken.da_code == da_code,
            RdlRefreshToken.revoked.is_(False),
            RdlRefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.first() is not None


async def _revoke_all_sessions(db: AsyncSession, da_code: str) -> None:
    """Revoke every active refresh token belonging to a DA."""
    await db.execute(
        update(RdlRefreshToken)
        .where(
            RdlRefreshToken.da_code == da_code,
            RdlRefreshToken.revoked.is_(False),
        )
        .values(revoked=True)
    )


async def _issue_tokens(db: AsyncSession, da_code: str) -> tuple[str, str]:
    """Create an access/refresh token pair and persist the hashed refresh token.

    The plain refresh token is returned to the caller and never stored.
    """
    access_token = create_access_token(da_code)
    refresh_token = generate_refresh_token()

    db.add(
        RdlRefreshToken(
            da_code=da_code,
            token=hash_refresh_token(refresh_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_EXPIRE_DAYS),
        )
    )
    return access_token, refresh_token


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate a DA and issue an access/refresh token pair.

    Single-device policy: if the DA already has an active session and
    `allow_multi_device` is off, the request is rejected with 409 so the client
    can confirm. Sending `force=true` logs the other device out and proceeds.
    """
    credential = await _get_credential(db, payload.da_code)

    # Verify identity. The same message is used for unknown DA and wrong
    # password so an attacker cannot tell which one was wrong.
    if credential is None or not verify_password(
        payload.password, credential.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid da_code or password",
        )

    if credential.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked. Contact admin.",
        )

    # Single-device policy
    if not credential.allow_multi_device:
        if not payload.force and await _has_active_session(db, credential.da_code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Already logged in on another device. "
                    "Confirm to log out the other device."
                ),
            )
        await _revoke_all_sessions(db, credential.da_code)

    access_token, refresh_token = await _issue_tokens(db, credential.da_code)
    await db.commit()

    return APIResponse(
        message="Login successful",
        data=LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            must_reset=credential.must_reset,
        ),
    )


@router.post("/refresh", response_model=APIResponse[RefreshResponse])
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Issue a new access token from a valid refresh token."""
    token_hash = hash_refresh_token(payload.refresh_token)

    result = await db.execute(
        select(RdlRefreshToken).where(RdlRefreshToken.token == token_hash)
    )
    stored = result.scalar_one_or_none()

    if stored is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Revoked means either an explicit logout or a login from another device.
    if stored.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ended. Your account may have been used on another device.",
        )

    if stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired. Please log in again.",
        )

    return APIResponse(
        message="Token refreshed",
        data=RefreshResponse(access_token=create_access_token(stored.da_code)),
    )


@router.post("/logout", response_model=APIResponse)
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Revoke the given refresh token.

    Always reports success so the endpoint cannot be used to probe which
    tokens exist.
    """
    token_hash = hash_refresh_token(payload.refresh_token)

    result = await db.execute(
        select(RdlRefreshToken).where(RdlRefreshToken.token == token_hash)
    )
    stored = result.scalar_one_or_none()

    if stored is not None and not stored.revoked:
        stored.revoked = True
        await db.commit()

    return APIResponse(message="Logged out successfully")


@router.post("/change-password", response_model=APIResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Change the authenticated DA's password and end all other sessions."""
    credential = await _get_credential(db, current_da.da_code)

    if credential is None or not verify_password(
        payload.old_password, credential.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Old password is incorrect",
        )

    credential.password_hash = hash_password(payload.new_password)
    credential.must_reset = False

    # A password change invalidates existing sessions, so any device holding an
    # old refresh token is logged out.
    await _revoke_all_sessions(db, credential.da_code)
    await db.commit()

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