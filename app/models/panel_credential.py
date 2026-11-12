from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.panel_user import RdlPanelUser


class RdlPanelCredential(Base, TimestampMixin):
    __tablename__ = "rdl_panel_credential"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # unique makes the one-to-one real in the database, not just in Python
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rdl_panel_user.id", ondelete="CASCADE"), unique=True
    )
    password_hash: Mapped[str] = mapped_column(String(255))
    # New accounts get a password from an admin, so they must change it on first login
    must_reset: Mapped[bool] = mapped_column(Boolean, server_default=true())
    is_locked: Mapped[bool] = mapped_column(Boolean, server_default=false())
    allow_multi_device: Mapped[bool] = mapped_column(Boolean, server_default=false())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["RdlPanelUser"] = relationship(back_populates="credential")