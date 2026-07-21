from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Index, Date, Numeric, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.customer import RplCustomerList
    from app.models.user import RdlUserList
    from app.models.material import RplMaterialList
    from app.models.overdue import RdlOverdue
    from app.models.payment import RdlPaymentHistory
    from app.models.delivery_return_item import RdlDeliveryReturnItem

class RdlDeliveryCollection(Base, TimestampMixin):
    __tablename__ = "rdl_delivery_collection"
    __table_args__ = (
        Index("ix_delivery_da_date", "da_code", "billing_date"),
        Index("ix_delivery_customer_date", "customer_id", "billing_date"),
    )
    
    billing_doc_no: Mapped[str] = mapped_column(String(10), primary_key=True)
    gate_pass_no: Mapped[str] = mapped_column(String(10))
    billing_date: Mapped[date] = mapped_column(Date)
    customer_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rpl_customer_list.customer_id", ondelete="RESTRICT")
    )
    da_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rdl_user_list.da_code", ondelete="RESTRICT")
    )
    billing_type: Mapped[str] = mapped_column(String(4))
    plant: Mapped[str] = mapped_column(String(4))
    sales_type: Mapped[str] = mapped_column(String(2))
    sales_org: Mapped[str] = mapped_column(String(4))
    delv_no: Mapped[str] = mapped_column(String(10))
    vehicle_no: Mapped[str] = mapped_column(String(25))
    billing_method: Mapped[str | None] = mapped_column(String(10), nullable=True)
    company_code: Mapped[str] = mapped_column(String(10))
    assignment: Mapped[str] = mapped_column(String(10))
    reference: Mapped[str] = mapped_column(String(20))
    item_category: Mapped[str] = mapped_column(String(10))
    delivery_status:Mapped[bool] = mapped_column(Boolean, default=False)
    delivery_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cash_collection_status:Mapped[bool] = mapped_column(Boolean, default=False)
    cash_collection_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    delivery_longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    cash_collection_latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    cash_collection_longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    invoice_value: Mapped[Decimal] = mapped_column(Numeric(18,2))
    cash_collection_value: Mapped[Decimal | None] = mapped_column(Numeric(18,2), nullable=True)
    round_down: Mapped[Decimal | None] = mapped_column(Numeric(6,2), nullable=True)
    return_status:Mapped[bool] = mapped_column(Boolean, default=False)
    return_value: Mapped[Decimal | None] = mapped_column(Numeric(18,2), nullable=True)
    due_status:Mapped[bool] = mapped_column(Boolean, default=False)
    due_value: Mapped[Decimal | None] = mapped_column(Numeric(18,2), nullable=True)
    return_type: Mapped[str | None] = mapped_column(String(10), nullable=True)
    
    customer: Mapped["RplCustomerList"] = relationship(back_populates="invoices")
    user: Mapped["RdlUserList"] = relationship(back_populates="invoices")
    items: Mapped[list["RdlDeliveryReturnItem"]] = relationship(back_populates="invoice")
    overdue: Mapped["RdlOverdue"] = relationship(back_populates="invoice")
    cash_collection: Mapped[list["RdlPaymentHistory"]] = relationship(back_populates="invoice")
  