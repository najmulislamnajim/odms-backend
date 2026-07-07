from datetime import date 
from decimal import Decimal

from sqlalchemy import String, Boolean, Integer, Date, Text, Numeric 
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin

class RplUserList(Base, TimestampMixin):
    __tablename__ = "rpl_user_list"
    
    work_area_t: Mapped[str] = mapped_column(String(10), primary_key=True)
    rm_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    zm_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sm_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    gm_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    rm_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    zm_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sm_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gm_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sap_user_code: Mapped[str] = mapped_column(String(10))
    sap_next_user_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(55))
    address: Mapped[str] = mapped_column(String(255))
    mobile_no: Mapped[str] = mapped_column(String(15))
    designation_id: Mapped[int] = mapped_column(Integer)
    designation: Mapped[str] = mapped_column(String(55))
    group_name: Mapped[str] = mapped_column(String(55))
    active: Mapped[bool] = mapped_column(Boolean, default=True)