from sqlalchemy import Boolean, ForeignKey, Integer, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.db.mixins import TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.depot import RdlDepotList
    from app.models.role import RdlRole
    from app.models.panel_credential import RdlPanelCredential


class RdlPanelUser(Base, TimestampMixin):
    """Admin and depot panel account. Depot accounts use the depot_code as username."""

    __tablename__ = "rdl_panel_user"

    # Surrogate key: username may be renamed, the id never changes
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    mobile_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    role_code: Mapped[str] = mapped_column(
        String(30), ForeignKey("rdl_role.role_code", ondelete="RESTRICT"), index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, server_default=true())
    # Null only for the first system admin, who is seeded rather than created
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("rdl_panel_user.id", ondelete="SET NULL"), nullable=True
    )

    role: Mapped["RdlRole"] = relationship(back_populates="users")
    creator: Mapped["RdlPanelUser | None"] = relationship(remote_side=[id])
    # Used only when the role has all_depot_access = False
    depots: Mapped[list["RdlDepotList"]] = relationship(secondary="rdl_panel_user_depot")
    credential: Mapped["RdlPanelCredential | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class RdlPanelUserDepot(Base, TimestampMixin):
    """Depots a panel user may see, flattened (no warehouse/hub tree)."""

    __tablename__ = "rdl_panel_user_depot"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rdl_panel_user.id", ondelete="CASCADE"), primary_key=True
    )
    depot_code: Mapped[str] = mapped_column(
        String(10), ForeignKey("rdl_depot_list.depot_code", ondelete="RESTRICT"),
        primary_key=True, index=True,
    )