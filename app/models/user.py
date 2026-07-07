from datetime import date

from sqlalchemy import String, Boolean, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class RdlUserList(Base, TimestampMixin):
    __tablename__ = "rdl_user_list"

    da_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    da_name: Mapped[str] = mapped_column(String(100))
    mobile_no: Mapped[str] = mapped_column(String(15))
    user_type: Mapped[str] = mapped_column(String(20))
    designation: Mapped[str] = mapped_column(String(50))
    depot_code: Mapped[str] = mapped_column(String(10), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
class RdlUserHistory(Base, TimestampMixin):
    __tablename__ = "rdl_user_depot_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(String(10))
    depot_code: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)