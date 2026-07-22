from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import RdlUserList

security = HTTPBearer()


async def get_current_da(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> RdlUserList:
    """Extract and validate the JWT token, returning the current DA."""
    token = credentials.credentials
    da_code = decode_access_token(token)

    if da_code is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    result = await db.execute(
        select(RdlUserList).where(RdlUserList.da_code == da_code)
    )
    da = result.scalar_one_or_none()

    if da is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DA not found",
        )

    return da
