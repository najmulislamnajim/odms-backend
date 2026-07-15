from datetime import date 
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, Date, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.delivery_collection import RdlDeliveryCollection
    from app.models.customer import RplCustomerList

class RdlOverdue(Base, TimestampMixin):
    __tablename__ = "rdl_overdue"
    __table_args__ = (
        Index("ix_overdue_customer_date", "customer_id", "billing_date"),
    )
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    billing_doc_no:Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rdl_delivery_collection.billing_doc_no", ondelete="RESTRICT")
    )
    billing_date:Mapped[date] = mapped_column(Date)
    customer_id:Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rpl_customer_list.customer_id", ondelete="RESTRICT")
    )
    due_amount:Mapped[Decimal] = mapped_column(Numeric(18,2))
    
    invoice: Mapped["RdlDeliveryCollection"] = relationship(back_populates="overdue")
    customer: Mapped["RplCustomerList"] = relationship(back_populates="overdue")
    