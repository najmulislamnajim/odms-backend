from datetime import date
from decimal import Decimal

from sqlalchemy import String, Numeric, Integer, Date, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.delivery_collection import RdlDeliveryCollection
    from app.models.user import RdlUserList 
    from app.models.customer import RplCustomerList


class RdlPaymentHistory(Base, TimestampMixin):
    __tablename__ = "rdl_payment_history"
    __table_args__ = (
        Index("ix_payment_da_date", "da_code", "payment_date"),
        Index("ix_payment_customer_date", "customer_id", "payment_date"),
    )
    
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    billing_doc_no:Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rdl_delivery_collection.billing_doc_no", ondelete="RESTRICT")
    )
    da_code:Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rdl_user_list.da_code", ondelete="RESTRICT")
    )
    customer_id:Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rpl_customer_list.customer_id", ondelete="RESTRICT")
    )
    amount:Mapped[Decimal] = mapped_column(Numeric(18,2))
    payment_type:Mapped[str] = mapped_column(String(10)) # regular, overdue
    payment_date:Mapped[date] = mapped_column(Date)
    
    invoice: Mapped["RdlDeliveryCollection"] = relationship(back_populates="cash_collection")
    user: Mapped["RdlUserList"] = relationship(back_populates="cash_collections")
    customer: Mapped["RplCustomerList"] = relationship(back_populates="payments")
    