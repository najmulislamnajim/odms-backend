from datetime import date 
from decimal import Decimal

from sqlalchemy import String, Boolean, Integer, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin

class RplMaterialList(Base, TimestampMixin):
    __tablename__ = "rpl_material_list"

    material_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    material_name: Mapped[str] = mapped_column(String(100))
    plant_code: Mapped[str] = mapped_column(String(10))
    sales_org: Mapped[str] = mapped_column(String(10))
    distribution_channel: Mapped[str] = mapped_column(String(10))
    producer_company: Mapped[str] = mapped_column(String(10))
    team: Mapped[str] = mapped_column(String(10))
    pack_size: Mapped[str] = mapped_column(String(20))
    unit_tp: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    unit_vat: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    mrp: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    brand_name: Mapped[str] = mapped_column(String(10))
    brand_description: Mapped[str] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(Boolean, default=True)