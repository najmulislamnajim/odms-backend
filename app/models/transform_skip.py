from sqlalchemy import String, Integer, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.db.mixins import TimestampMixin


class RdlTransformSkip(Base, TimestampMixin):
    __tablename__ = "rdl_transform_skip"
    __table_args__ = (
        Index("ix_transform_skip_resolved", "resolved"),
        Index("ix_transform_skip_sync_date", "sync_date"),
        UniqueConstraint("billing_doc_no", "sync_date", name="uq_transform_skip_invoice_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    billing_doc_no: Mapped[str] = mapped_column(String(10))
    customer_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    da_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    reason: Mapped[str] = mapped_column(String(30)) 
    sync_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)