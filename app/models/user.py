from datetime import date

from sqlalchemy import String, Boolean, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user_credential import RdlUserCredential
    from app.models.depot import RdlDepotList
    from app.models.attendance import RdlAttendance
    from app.models.conveyance import RdlConveyance
    from app.models.customer_visit import RdlCustomerVisit
    from app.models.delivery_collection import RdlDeliveryCollection
    from app.models.payment import RdlPaymentHistory

class RdlUserList(Base, TimestampMixin):
    __tablename__ = "rdl_user_list"

    da_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    da_name: Mapped[str] = mapped_column(String(100))
    mobile_no: Mapped[str] = mapped_column(String(15))
    user_type: Mapped[str] = mapped_column(String(20))
    designation: Mapped[str] = mapped_column(String(50))
    depot_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_depot_list.depot_code", ondelete="RESTRICT"), 
        index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    depot:Mapped["RdlDepotList | None"] = relationship(back_populates="users")
    credential: Mapped["RdlUserCredential | None"] = relationship(back_populates="user")
    depot_history: Mapped[list["RdlUserHistory"]] = relationship(back_populates="user")
    attendances: Mapped[list["RdlAttendance"]] = relationship(back_populates="user")
    conveyances: Mapped[list["RdlConveyance"]] = relationship(back_populates="user")
    customer_visits: Mapped[list["RdlCustomerVisit"]] = relationship(back_populates="user")
    invoices: Mapped[list["RdlDeliveryCollection"]] = relationship(back_populates="user")
    cash_collections: Mapped[list["RdlPaymentHistory"]] = relationship(back_populates="user")
    
    
class RdlUserHistory(Base, TimestampMixin):
    __tablename__ = "rdl_user_depot_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    da_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_user_list.da_code", ondelete="RESTRICT")
    )
    depot_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("rdl_depot_list.depot_code", ondelete="RESTRICT")
    )
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    user: Mapped["RdlUserList"] = relationship(back_populates="depot_history")
    depot: Mapped["RdlDepotList"] = relationship(back_populates="user_depot_history")