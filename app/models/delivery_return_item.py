from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.material import RplMaterialList
    from app.models.delivery_collection import RdlDeliveryCollection

class RdlDeliveryReturnItem(Base, TimestampMixin):
    __tablename__ = "rdl_delivery_return_item"
    __table_args__ = (
        UniqueConstraint("billing_doc_no", "material_id", "batch", name="uq_delivery_collection_billing_doc_material_batch"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    billing_doc_no: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rdl_delivery_collection.billing_doc_no", ondelete="RESTRICT"),
        index=True
    )
    material_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rpl_material_list.material_id", ondelete="RESTRICT")
    )
    batch: Mapped[str] = mapped_column(String(10))
    # Snapshot of the material name, producer company, team, quantity, tp, vat
    # denormalized for better performance in simple reports.
    material_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    producer_company: Mapped[str | None] = mapped_column(String(10), nullable=True)
    team: Mapped[str | None] = mapped_column(String(4), nullable=True)
    tp: Mapped[Decimal] = mapped_column(Numeric(18,2))
    vat: Mapped[Decimal] = mapped_column(Numeric(18,2))
    quantity: Mapped[int] = mapped_column(Integer)
    net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))
    delivery_quantity: Mapped[int] = mapped_column(Integer)
    return_quantity: Mapped[int] = mapped_column(Integer)
    delivery_net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))
    return_net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))
    invoice: Mapped["RdlDeliveryCollection"] = relationship(back_populates="items")
    material: Mapped["RplMaterialList"] = relationship(back_populates="invoice_material")
    