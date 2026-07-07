from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, Index, Integer, Date, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin

class RplSalesInfoSap(Base, TimestampMixin):
    __tablename__ = "rpl_sales_info_sap"
    __table_args__ = (
        UniqueConstraint("billing_doc_no", "billing_date", "material_id", "batch", name="uq_sales_info_billing_doc_date_material_batch"),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    gate_pass_no: Mapped[str] = mapped_column(String(10))
    billing_doc_no: Mapped[str] = mapped_column(String(10))
    billing_date: Mapped[date] = mapped_column(Date)
    customer_id: Mapped[str] = mapped_column(String(10))
    material_id: Mapped[str] = mapped_column(String(10))
    batch: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    tp: Mapped[Decimal] = mapped_column(Numeric(18,2))
    vat: Mapped[Decimal] = mapped_column(Numeric(18,2))
    net_val: Mapped[Decimal] = mapped_column(Numeric(18,2))
    billing_type: Mapped[str] = mapped_column(String(4))
    plant: Mapped[str] = mapped_column(String(4))
    sales_org: Mapped[str] = mapped_column(String(4))
    sales_type: Mapped[str] = mapped_column(String(2))
    team: Mapped[str] = mapped_column(String(4))
    company_code: Mapped[str] = mapped_column(String(4))
    assignment: Mapped[str] = mapped_column(String(10))
    territory_code: Mapped[str] = mapped_column(String(5))
    reference: Mapped[str] = mapped_column(String(16))
    order_type: Mapped[str] = mapped_column(String(5), nullable=True)
    item_category: Mapped[str] = mapped_column(String(4))
    cancel: Mapped[str] = mapped_column(String(1), nullable=True)
    mio_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mio_mobile_no: Mapped[str | None] = mapped_column(String(15), nullable=True)
    