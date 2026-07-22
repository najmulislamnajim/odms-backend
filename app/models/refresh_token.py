from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.mixins import TimestampMixin


class RdlRefreshToken(Base, TimestampMixin):
    __tablename__ = "rdl_refresh_token"
    __table_args__ = (
        Index("ix_refresh_token_da_code", "da_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("rdl_user_list.da_code", ondelete="CASCADE")
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(default=False)