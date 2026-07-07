from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Index, Integer, Date, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin

class RdlConveyance(Base, TimestampMixin):
    __tablename__ = "rdl_conveyance"
    __table_args__ = (
        Index("ix_conveyance_da_date", "da_code", "working_date"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(String(10))
    working_date: Mapped[date] = mapped_column(Date)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    start_longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    end_latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    end_longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    travel_duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10,2), nullable=True)
    vehicle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    start_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    end_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)