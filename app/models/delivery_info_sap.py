from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Integer, Date, Index
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin

class RdlDeliveryInfoSap(Base, TimestampMixin):
    __tablename__ = "rdl_delivery_info_sap"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    billing_doc_no: Mapped[str] = mapped_column(String(10), unique=True)
    billing_date: Mapped[date] = mapped_column(Date, index=True)
    delv_no: Mapped[str] = mapped_column(String(10))
    vehicle_no: Mapped[str] = mapped_column(String(25))
    da_code: Mapped[str] = mapped_column(String(10))
    da_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    