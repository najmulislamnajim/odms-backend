# Python Imports
from datetime import datetime, timedelta, timezone

# SQLAlchemy Imports
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RdlRefreshToken
from app.models.user_credential import RdlUserCredential
from app.schemas.auth import LoginResponse

# Checked against when the DA does not exist, so an unknown da_code takes as
# long as a wrong password and response time does not reveal valid codes.
_DUMMY_HASH = hash_password("timing-safe-dummy-password")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_credential(db: AsyncSession, da_code: str) -> RdlUserCredential | None:
    result = await db.execute(
        select(RdlUserCredential).where(RdlUserCredential.da_code == da_code)
    )
    return result.scalar_one_or_none()


async def _get_refresh_token(db: AsyncSession, plain_token: str) -> RdlRefreshToken | None:
    result = await db.execute(
        select(RdlRefreshToken).where(RdlRefreshToken.token == hash_refresh_token(plain_token))
    )
    return result.scalar_one_or_none()


async def _has_active_session(db: AsyncSession, da_code: str) -> bool:
    """True if the DA already has a refresh token that is not revoked or expired."""
    result = await db.execute(
        select(RdlRefreshToken.id).where(
            RdlRefreshToken.da_code == da_code,
            RdlRefreshToken.revoked.is_(False),
            RdlRefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    return result.first() is not None


async def _revoke_all_sessions(db: AsyncSession, da_code: str) -> None:
    await db.execute(
        update(RdlRefreshToken)
        .where(RdlRefreshToken.da_code == da_code, RdlRefreshToken.revoked.is_(False))
        .values(revoked=True)
    )


def _issue_tokens(db: AsyncSession, da_code: str) -> tuple[str, str]:
    """Create an access/refresh pair; only the refresh token's hash is stored."""
    access_token = create_access_token(da_code)
    refresh_token = generate_refresh_token()
    db.add(
        RdlRefreshToken(
            da_code=da_code,
            token=hash_refresh_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_EXPIRE_DAYS),
        )
    )
    return access_token, refresh_token


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

async def login(db: AsyncSession, da_code: str, password: str, force: bool) -> LoginResponse:
    """Verify credentials and issue tokens, enforcing the single-device policy.

    Without allow_multi_device, a second login is refused with 409 unless
    force=True, which logs the other device out.
    """
    credential = await _get_credential(db, da_code)

    # Always run one hash check, even for an unknown DA (see _DUMMY_HASH)
    password_ok = verify_password(
        password, credential.password_hash if credential else _DUMMY_HASH
    )
    if credential is None or not password_ok:
        raise UnauthorizedError("Invalid da_code or password")

    if credential.is_locked:
        raise ForbiddenError("Account is locked. Contact admin.")

    if not credential.allow_multi_device:
        if not force and await _has_active_session(db, da_code):
            raise ConflictError(
                "Already logged in on another device. Confirm to log out the other device."
            )
        await _revoke_all_sessions(db, da_code)

    access_token, refresh_token = _issue_tokens(db, da_code)
    await db.commit()
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        must_reset=credential.must_reset,
    )


async def refresh(db: AsyncSession, refresh_token: str) -> str:
    """Return a new access token for a valid refresh token."""
    stored = await _get_refresh_token(db, refresh_token)
    if stored is None:
        raise UnauthorizedError("Invalid refresh token")

    # Revoked means an explicit logout or a login from another device
    if stored.revoked:
        raise UnauthorizedError(
            "Session ended. Your account may have been used on another device."
        )
    if stored.expires_at < datetime.now(timezone.utc):
        raise UnauthorizedError("Refresh token expired. Please log in again.")

    # A lock must stop existing sessions too, not only new logins
    credential = await _get_credential(db, stored.da_code)
    if credential is None or credential.is_locked:
        raise ForbiddenError("Account is locked. Contact admin.")

    return create_access_token(stored.da_code)


async def logout(db: AsyncSession, refresh_token: str) -> None:
    """Revoke a refresh token. Silent when the token is unknown, so it can't be probed."""
    stored = await _get_refresh_token(db, refresh_token)
    if stored is not None and not stored.revoked:
        stored.revoked = True
        await db.commit()


async def change_password(
    db: AsyncSession, da_code: str, old_password: str, new_password: str
) -> None:
    """Change the password and end every session, including other devices."""
    credential = await _get_credential(db, da_code)
    if credential is None or not verify_password(old_password, credential.password_hash):
        raise UnauthorizedError("Old password is incorrect")

    credential.password_hash = hash_password(new_password)
    credential.must_reset = False
    await _revoke_all_sessions(db, da_code)
    await db.commit()