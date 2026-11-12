from decimal import Decimal

from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.user import RdlUserList, RdlUserHistory
    from app.models.route import RdlRouteList, RdlRouteHistory
    
    
class RdlDepotList(Base, TimestampMixin):
    __tablename__ = "rdl_depot_list"

    depot_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    depot_name: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    mobile_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    users: Mapped[list["RdlUserList"]] = relationship(back_populates="depot")
    user_depot_history: Mapped[list["RdlUserHistory"]] = relationship(back_populates="depot")
    routes: Mapped[list["RdlRouteList"]] = relationship(back_populates="depot")
    route_depot_history: Mapped[list["RdlRouteHistory"]] = relationship(back_populates="depot")