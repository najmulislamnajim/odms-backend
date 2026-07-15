from sqlalchemy import String, Boolean 
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
    
    users: Mapped[list["RdlUserList"]] = relationship(back_populates="depot")
    user_depot_history: Mapped[list["RdlUserHistory"]] = relationship(back_populates="depot")
    routes: Mapped[list["RdlRouteList"]] = relationship(back_populates="depot")
    route_depot_history: Mapped[list["RdlRouteHistory"]] = relationship(back_populates="depot")