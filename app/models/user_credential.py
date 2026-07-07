from datetime import date 

from sqlalchemy import String, Boolean, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
    
class RdlUserCredential(Base, TimestampMixin):
    __tablename__ = "rdl_user_credential"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(String(10), index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    must_reset: Mapped[bool] = mapped_column(Boolean, default=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)