from datetime import datetime, date 
from decimal import Decimal

from sqlalchemy import String, Integer, DateTime, Numeric, Index, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship 

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.user import RdlUserList
    from app.models.customer import RplCustomerList

class RdlCustomerVisit(Base, TimestampMixin):
    __tablename__ = "rdl_customer_visit"
    __table_args__ = (
        Index("ix_visit_customer_date", "customer_id", "working_date"),
        Index("ix_visit_da_date", "da_code", "working_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_user_list.da_code", ondelete="RESTRICT")
    )        
    customer_id: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rpl_customer_list.customer_id", ondelete="RESTRICT")
    )   
    working_date: Mapped[date] = mapped_column(Date)
    visit_type: Mapped[str] = mapped_column(String(10))
    visit_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    user: Mapped["RdlUserList"] = relationship(back_populates="customer_visits")
    customer: Mapped["RplCustomerList"] = relationship(back_populates="customer_visits")