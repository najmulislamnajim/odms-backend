# Python Imports
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

# SQLAlchemy Imports
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.delivery_collection import RdlDeliveryCollection
from app.models.overdue import RdlOverdue
from app.models.payment import RdlPaymentHistory
from app.schemas.collection import CollectionRequest
from app.services.delivery.collection_logic import split_round_down

ZERO = Decimal("0.00")


@dataclass
class CollectionResult:
    """What a successful collection produced, independent of any API format."""

    customer_id: str
    collected_amount: Decimal
    round_down: Decimal
    invoice_count: int


async def list_pending(
    db: AsyncSession, da_code: str, customer_id: str, billing_date: date
) -> list[RdlDeliveryCollection]:
    """Return a customer's delivered-but-uncollected invoices for a date."""
    stmt = (
        select(RdlDeliveryCollection)
        .where(
            RdlDeliveryCollection.da_code == da_code,
            RdlDeliveryCollection.customer_id == customer_id,
            RdlDeliveryCollection.billing_date == billing_date,
            RdlDeliveryCollection.delivery_status.is_(True),
            RdlDeliveryCollection.cash_collection_status.is_(False),
            RdlDeliveryCollection.due_value > 0,
        )
        .order_by(RdlDeliveryCollection.billing_doc_no)
    )
    return list((await db.execute(stmt)).scalars().all())


async def collect_cash(
    db: AsyncSession,
    da_code: str,
    payload: CollectionRequest,
    now: datetime | None = None,
) -> CollectionResult:
    """Collect cash across the selected invoices in one atomic operation.

    The total is rounded down to whole taka and the dropped paisa is split
    across invoices by split_round_down. Current-day invoices only.
    """
    now = now or datetime.now(timezone.utc)
    today = now.date()

    # --- Load the selected invoices ---
    stmt = select(RdlDeliveryCollection).where(
        RdlDeliveryCollection.da_code == da_code,
        RdlDeliveryCollection.customer_id == payload.customer_id,
        RdlDeliveryCollection.billing_doc_no.in_(payload.billing_doc_nos),
    )
    invoices = (await db.execute(stmt)).scalars().all()
    by_doc = {inv.billing_doc_no: inv for inv in invoices}

    # --- Gate 1: every requested invoice must exist for this DA/customer ---
    unknown = set(payload.billing_doc_nos) - set(by_doc)
    if unknown:
        raise NotFoundError(f"Invoice(s) not found for this customer: {sorted(unknown)}")

    # --- Gate 2: all delivered ---
    not_delivered = [d for d, inv in by_doc.items() if not inv.delivery_status]
    if not_delivered:
        raise BadRequestError(f"Not delivered yet: {sorted(not_delivered)}")

    # --- Gate 3: none already collected (duplicate protection) ---
    already = [d for d, inv in by_doc.items() if inv.cash_collection_status]
    if already:
        raise ConflictError(f"Already collected: {sorted(already)}")

    # --- Gate 4: current-day only; older invoices go through the overdue flow ---
    overdue_docs = [d for d, inv in by_doc.items() if inv.billing_date < today]
    if overdue_docs:
        raise BadRequestError(
            "These invoices are overdue and must be collected through the "
            f"overdue flow: {sorted(overdue_docs)}"
        )

    # --- Round down the total, then split the dropped paisa ---
    ordered = [by_doc[doc] for doc in payload.billing_doc_nos]
    dues = [inv.due_value for inv in ordered]
    round_downs = split_round_down(dues)

    total_round_down = sum(round_downs, ZERO)
    total_collect = sum(dues, ZERO) - total_round_down

    for inv, round_down in zip(ordered, round_downs):
        collection_value = inv.due_value - round_down

        inv.cash_collection_value = collection_value
        inv.round_down = round_down
        inv.cash_collection_status = True
        inv.cash_collection_datetime = now
        inv.cash_collection_latitude = payload.latitude
        inv.cash_collection_longitude = payload.longitude
        inv.due_value = ZERO
        inv.due_status = False

        db.add(
            RdlPaymentHistory(
                billing_doc_no=inv.billing_doc_no,
                da_code=da_code,
                customer_id=payload.customer_id,
                amount=collection_value,
                payment_type="regular",
                payment_date=today,
            )
        )

    # --- Remove any overdue rows for these invoices (now paid) ---
    await db.execute(
        delete(RdlOverdue).where(RdlOverdue.billing_doc_no.in_(payload.billing_doc_nos))
    )

    await db.commit()

    return CollectionResult(
        customer_id=payload.customer_id,
        collected_amount=total_collect,
        round_down=total_round_down,
        invoice_count=len(ordered),
    )