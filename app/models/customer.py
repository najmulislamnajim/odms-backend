from datetime import date 
from decimal import Decimal

from sqlalchemy import String, Boolean, Integer, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
    
    
class RplCustomerList(Base, TimestampMixin):
    __tablename__ = "rpl_customer_list"

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    shop_name: Mapped[str] = mapped_column(String(100))
    customer_name: Mapped[str] = mapped_column(String(100))
    mobile_no: Mapped[str] = mapped_column(String(15))
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    street: Mapped[str] = mapped_column(Text)
    post_code: Mapped[str] = mapped_column(String(10))
    upazila: Mapped[str] = mapped_column(String(50))
    district: Mapped[str] = mapped_column(String(50))
    drug_reg_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customer_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    route_code: Mapped[str] = mapped_column(String(10), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
class RplCustomerSalesOrg(Base, TimestampMixin):
    __tablename__ = "rpl_customer_sales_org"

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    company_code: Mapped[str] = mapped_column(String(10))
    sales_org: Mapped[str] = mapped_column(String(10), primary_key=True)
    del_plant: Mapped[str] = mapped_column(String(10), primary_key=True)
    pre_cust_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    
class RplCustomerTerritory(Base, TimestampMixin):
    __tablename__ = "rpl_customer_territory"

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    team: Mapped[str] = mapped_column(String(10), primary_key=True)
    work_area: Mapped[str] = mapped_column(String(10), primary_key=True)
    start_date: Mapped[date] = mapped_column(Date, primary_key=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
class RplCustomerRouteHistory(Base, TimestampMixin):
    __tablename__ = "rpl_customer_route_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(10))
    route_code: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
class RdlCustomerLocation(Base, TimestampMixin):
    __tablename__ = "rdl_customer_location"
    
    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9,6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(9,6))
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
