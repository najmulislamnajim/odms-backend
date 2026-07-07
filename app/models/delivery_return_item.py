from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Index, Integer, Date, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin

class RdlDeliveryReturnItem(Base, TimestampMixin):
    __tablename__ = "rdl_delivery_return_item"
    __table_args__ = (
        UniqueConstraint("billing_doc_no", "material_id", "batch", name="uq_delivery_collection_billing_doc_material_batch"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    billing_doc_no: Mapped[str] = mapped_column(String(10), index=True)
    material_id: Mapped[str] = mapped_column(String(10))
    batch: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    tp: Mapped[Decimal] = mapped_column(Numeric(18,2))
    vat: Mapped[Decimal] = mapped_column(Numeric(18,2))
    net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))
    delivery_quantity: Mapped[int] = mapped_column(Integer)
    return_quantity: Mapped[int] = mapped_column(Integer)
    delivery_net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))
    return_net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))