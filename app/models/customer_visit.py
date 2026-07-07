from datetime import datetime, date 
from decimal import Decimal

from sqlalchemy import String, Integer, DateTime, Numeric, Index, UniqueConstraint, Text, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class RdlCustomerVisit(Base, TimestampMixin):
    __tablename__ = "rdl_customer_visit"
    __table_args__ = (
        Index("ix_visit_customer_date", "customer_id", "working_date"),
        Index("ix_visit_da_date", "da_code", "working_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(String(10))        
    customer_id: Mapped[str] = mapped_column(String(10))   
    visit_type: Mapped[str] = mapped_column(String(10))
    working_date: Mapped[date] = mapped_column(Date)
    visit_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    start_latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    start_longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)