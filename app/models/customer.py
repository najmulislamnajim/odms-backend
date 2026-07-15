from datetime import date 
from decimal import Decimal

from sqlalchemy import String, Boolean, Integer, Date, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.customer_visit import RdlCustomerVisit 
    from app.models.route import RdlRouteList
    from app.models.delivery_collection import RdlDeliveryCollection
    from app.models.overdue import RdlOverdue
    from app.models.payment import RdlPaymentHistory
    
    
class RplCustomerList(Base, TimestampMixin):
    __tablename__ = "rpl_customer_list"

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    shop_name: Mapped[str] = mapped_column(String(100))
    customer_name: Mapped[str] = mapped_column(String(100))
    route_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_route_list.route_code"), 
        index=True
    )
    mobile_no: Mapped[str] = mapped_column(String(15))
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    street: Mapped[str] = mapped_column(Text)
    post_code: Mapped[str] = mapped_column(String(10))
    upazila: Mapped[str] = mapped_column(String(50))
    district: Mapped[str] = mapped_column(String(50))
    drug_reg_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    customer_group: Mapped[str | None] = mapped_column(String(50), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    customer_visits: Mapped[list["RdlCustomerVisit"]] = relationship(back_populates="customer")
    route: Mapped["RdlRouteList"] = relationship(back_populates="customers")
    location: Mapped["RdlCustomerLocation"] = relationship(back_populates="customer")
    invoices: Mapped[list["RdlDeliveryCollection"]] = relationship(back_populates="customer")
    overdue: Mapped[list["RdlOverdue"]] = relationship(back_populates="customer")
    payments: Mapped[list["RdlPaymentHistory"]] = relationship(back_populates="customer")
    
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
    customer_id: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rpl_customer_list.customer_id", ondelete="RESTRICT")
    )
    route_code: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rdl_route_list.route_code")
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    routes: Mapped["RdlRouteList"] = relationship(back_populates="customers_route_history")
    
class RdlCustomerLocation(Base, TimestampMixin):
    __tablename__ = "rdl_customer_location"
    
    customer_id: Mapped[str] = mapped_column(
        String(10),
        ForeignKey("rpl_customer_list.customer_id"),
        primary_key=True
    )
    latitude: Mapped[Decimal] = mapped_column(Numeric(9,6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(9,6))
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    customer: Mapped["RplCustomerList"] = relationship(back_populates="location")
