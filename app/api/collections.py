# Python Imports
from datetime import date as date_type
from datetime import datetime, timezone
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

# FastAPI Imports
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

# SQLAlchemy Imports
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.api.deps import get_current_da
from app.db.session import get_db
from app.models.delivery_collection import RdlDeliveryCollection
from app.models.overdue import RdlOverdue
from app.models.payment import RdlPaymentHistory
from app.models.user import RdlUserList
from app.schemas.collection import CollectionRequest, PendingInvoice
from app.schemas.response import APIResponse
from app.services.collection_logic import split_round_down

router = APIRouter(prefix="/collections", tags=["collections"])

ZERO = Decimal("0.00")
ONE = Decimal("1")
CENT = Decimal("0.01")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paisa(amount: Decimal) -> Decimal:
    """Return the fractional (sub-taka) part of an amount, e.g. 500.90 -> 0.90."""
    return amount - amount.quantize(ONE, rounding=ROUND_DOWN)


# ---------------------------------------------------------------------------
# Pending list
# ---------------------------------------------------------------------------

@router.get("/pending/{customer_id}", response_model=APIResponse[list[PendingInvoice]])
async def list_pending_collections(
    customer_id: str = Path(..., description="Customer ID"),
    billing_date: date_type | None = Query(None, description="Defaults to today"),
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """List a customer's delivered-but-uncollected invoices for a date.

    Overdue (older) invoices are handled separately by the overdue flow.
    """
    target_date = billing_date or date_type.today()

    stmt = (
        select(RdlDeliveryCollection)
        .where(
            RdlDeliveryCollection.da_code == current_da.da_code,
            RdlDeliveryCollection.customer_id == customer_id,
            RdlDeliveryCollection.billing_date == target_date,
            RdlDeliveryCollection.delivery_status.is_(True),
            RdlDeliveryCollection.cash_collection_status.is_(False),
            RdlDeliveryCollection.due_value > 0,
        )
        .order_by(RdlDeliveryCollection.billing_doc_no)
    )
    invoices = (await db.execute(stmt)).scalars().all()

    pending = [
        PendingInvoice(
            billing_doc_no=inv.billing_doc_no,
            billing_date=inv.billing_date,
            invoice_value=inv.invoice_value,
            due_value=inv.due_value,
        )
        for inv in invoices
    ]

    return APIResponse(message=f"{len(pending)} pending invoice(s)", data=pending)


# ---------------------------------------------------------------------------
# Collect
# ---------------------------------------------------------------------------

@router.post("", response_model=APIResponse[dict])
async def collect_cash(
    payload: CollectionRequest,
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Collect cash across the selected invoices in one atomic operation.

    The total is rounded down to whole taka. The dropped paisa is shared out
    across the invoices in proportion to each invoice's own paisa, and the
    last invoice absorbs the remainder so the parts always sum exactly. This
    endpoint handles current-day collection only.
    """
    now = datetime.now(timezone.utc)
    today = now.date()

    # --- Load the selected invoices -----------------------------------------
    stmt = select(RdlDeliveryCollection).where(
        RdlDeliveryCollection.da_code == current_da.da_code,
        RdlDeliveryCollection.customer_id == payload.customer_id,
        RdlDeliveryCollection.billing_doc_no.in_(payload.billing_doc_nos),
    )
    invoices = (await db.execute(stmt)).scalars().all()
    by_doc = {inv.billing_doc_no: inv for inv in invoices}

    # --- Gate 1: every requested invoice must exist for this DA/customer -----
    unknown = set(payload.billing_doc_nos) - set(by_doc)
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice(s) not found for this customer: {sorted(unknown)}",
        )

    # --- Gate 2: all delivered ---------------------------------------------
    not_delivered = [d for d, inv in by_doc.items() if not inv.delivery_status]
    if not_delivered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not delivered yet: {sorted(not_delivered)}",
        )

    # --- Gate 3: none already collected (duplicate protection) --------------
    already = [d for d, inv in by_doc.items() if inv.cash_collection_status]
    if already:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Already collected: {sorted(already)}",
        )

    # --- Gate 4: current-day only; older invoices go through the overdue flow
    overdue_docs = [d for d, inv in by_doc.items() if inv.billing_date < today]
    if overdue_docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "These invoices are overdue and must be collected through the "
                f"overdue flow: {sorted(overdue_docs)}"
            ),
        )

    # --- Round down the total, then split the dropped paisa -----------------
    ordered = [by_doc[doc] for doc in payload.billing_doc_nos]
    dues = [inv.due_value for inv in ordered]
    round_downs = split_round_down(dues)

    total_collect = sum(dues, ZERO) - sum(round_downs, ZERO)
    total_round_down = sum(round_downs, ZERO)

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
                da_code=current_da.da_code,
                customer_id=payload.customer_id,
                amount=collection_value,
                payment_type="regular",
                payment_date=today,
            )
        )

    # --- Remove any overdue rows for these invoices (now paid) --------------
    await db.execute(
        delete(RdlOverdue).where(
            RdlOverdue.billing_doc_no.in_(payload.billing_doc_nos)
        )
    )

    await db.commit()

    return APIResponse(
        message=f"Collected {total_collect} from {len(ordered)} invoice(s)",
        data={
            "customer_id": payload.customer_id,
            "collected_amount": str(total_collect),
            "round_down": str(total_round_down),
            "invoice_count": len(ordered),
        },
    )