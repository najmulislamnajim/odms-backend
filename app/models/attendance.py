from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Date, Integer, DateTime, Numeric, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.user import RdlUserList

class RdlAttendance(Base, TimestampMixin):
    __tablename__ = "rdl_attendance"
    __table_args__ = (
        UniqueConstraint("da_code", "working_date", name="uq_attendance_da_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_user_list.da_code", ondelete="RESTRICT"), 
        index=True
    )
    working_date: Mapped[date] = mapped_column(Date)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    start_longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    end_latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    end_longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    late_time_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    over_time_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    end_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    user: Mapped["RdlUserList"] = relationship(back_populates="attendances")
    