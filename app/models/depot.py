from sqlalchemy import String, Boolean 
from sqlalchemy.orm import Mapped, mapped_column 

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
    
    
class RdlDepotList(Base, TimestampMixin):
    __tablename__ = "rdl_depot_list"

    depot_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    depot_name: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)