from datetime import date 

from sqlalchemy import String, Boolean, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.depot import RdlDepotList
    from app.models.customer import RplCustomerList, RplCustomerRouteHistory
    
class RdlRouteList(Base, TimestampMixin):
    __tablename__ = "rdl_route_list"

    route_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    route_name: Mapped[str] = mapped_column(String(100))
    depot_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_depot_list.depot_code", ondelete="RESTRICT")
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    depot: Mapped["RdlDepotList"] = relationship(back_populates="routes")
    depot_history: Mapped[list["RdlRouteHistory"]] = relationship(back_populates="route")
    customers: Mapped[list["RplCustomerList"]] = relationship(back_populates="route")
    customers_route_history: Mapped[list["RplCustomerRouteHistory"]] = relationship(back_populates="routes")

class RdlRouteHistory(Base, TimestampMixin):
    __tablename__ = "rdl_route_depot_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_code: Mapped[str] = mapped_column(String(10), ForeignKey("rdl_route_list.route_code", ondelete="RESTRICT"))
    depot_code: Mapped[str] = mapped_column(String(10), ForeignKey("rdl_depot_list.depot_code", ondelete="RESTRICT"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    route: Mapped["RdlRouteList"] = relationship(back_populates="depot_history")
    depot: Mapped["RdlDepotList"] = relationship(back_populates="route_depot_history")
    
