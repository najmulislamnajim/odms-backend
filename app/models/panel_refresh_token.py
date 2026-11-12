from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.mixins import TimestampMixin


class RdlPanelRefreshToken(Base, TimestampMixin):
    __tablename__ = "rdl_panel_refresh_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rdl_panel_user.id", ondelete="CASCADE"), index=True
    )
    # SHA-256 of the token; the plain token is only ever sent to the client
    token: Mapped[str] = mapped_column(String(255), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(Boolean, server_default=false())