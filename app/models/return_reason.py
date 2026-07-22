from decimal import Decimal

from sqlalchemy import String, Integer, Numeric, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base 
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.models.delivery_return_item import RdlDeliveryReturnItem

class RdlReturnReason(Base, TimestampMixin):
    __tablename__ = "rdl_return_reason"

    reason_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    reason_name: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    items: Mapped[list["RdlDeliveryReturnItem"]] = relationship(back_populates="return_reason")