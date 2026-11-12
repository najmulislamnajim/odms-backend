from sqlalchemy import Boolean, String, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.panel_user import RdlPanelUser


class RdlRole(Base, TimestampMixin):
    """Panel role. Names are corporate ranks; access comes from the flags, never the name."""

    __tablename__ = "rdl_role"

    role_code: Mapped[str] = mapped_column(String(30), primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50))
    # True: sees every depot. False: only depots assigned in rdl_panel_user_depot
    all_depot_access: Mapped[bool] = mapped_column(Boolean, server_default=false())
    # Developer role with every privilege (system-admin)
    is_system: Mapped[bool] = mapped_column(Boolean, server_default=false())
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())

    users: Mapped[list["RdlPanelUser"]] = relationship(back_populates="role")