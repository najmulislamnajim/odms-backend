from datetime import date 

from sqlalchemy import String, Boolean, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
    
class RdlRouteList(Base, TimestampMixin):
    __tablename__ = "rdl_route_list"

    route_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    route_name: Mapped[str] = mapped_column(String(100))
    depot_code: Mapped[str] = mapped_column(String(10))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class RdlRouteHistory(Base, TimestampMixin):
    __tablename__ = "rdl_route_depot_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_code: Mapped[str] = mapped_column(String(10))
    depot_code: Mapped[str] = mapped_column(String(10))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
