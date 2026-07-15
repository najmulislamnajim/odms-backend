from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import RdlUserList
    
class RdlUserCredential(Base, TimestampMixin):
    __tablename__ = "rdl_user_credential"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(String(10), ForeignKey("rdl_user_list.da_code", ondelete="CASCADE"), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    must_reset: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    user: Mapped["RdlUserList"] = relationship(back_populates="credential")