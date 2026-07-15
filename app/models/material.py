from datetime import date 
from decimal import Decimal

from sqlalchemy import String, Boolean, Integer, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.delivery_return_item import RdlDeliveryReturnItem

class RplMaterialList(Base, TimestampMixin):
    __tablename__ = "rpl_material_list"

    material_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    material_name: Mapped[str] = mapped_column(String(100))
    plant_code: Mapped[str] = mapped_column(String(10))
    sales_org: Mapped[str] = mapped_column(String(10))
    distribution_channel: Mapped[str | None] = mapped_column(String(10), nullable=True)
    producer_company: Mapped[str | None] = mapped_column(String(10), nullable=True)
    team: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pack_size: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_tp: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    unit_vat: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    mrp: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    brand_name: Mapped[str | None] = mapped_column(String(10), nullable=True)
    brand_description: Mapped[str | None] = mapped_column(String(50), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    invoice_material: Mapped[list["RdlDeliveryReturnItem"]] = relationship(back_populates="material")