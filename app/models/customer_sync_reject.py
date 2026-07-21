from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Boolean, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.mixins import TimestampMixin


class RdlCustomerSyncReject(Base, TimestampMixin):
    __tablename__ = "rdl_customer_sync_reject"
    __table_args__ = (
        Index("ix_customer_reject_resolved", "resolved"),
        UniqueConstraint("customer_id", "sync_date", name="uq_customer_sync_reject_customer_id_sync_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(10))
    route_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    shop_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str] = mapped_column(String(50))          # 'route_missing'
    sync_date: Mapped[str | None] = mapped_column(String(10), index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)  # admin route add korle True