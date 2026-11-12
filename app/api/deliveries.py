# Python Imports
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

# FastAPI Imports
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy Imports
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# App Imports
from app.api.deps import get_current_da
from app.db.session import get_db
from app.models.delivery_collection import RdlDeliveryCollection
from app.models.delivery_return_item import RdlDeliveryReturnItem
from app.models.user import RdlUserList
from app.schemas.delivery import DeliverySaveRequest
from app.schemas.response import APIResponse

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

ZERO = Decimal("0.00")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_value(net_val: Decimal, quantity: int, return_quantity: int) -> tuple[Decimal, Decimal]:
    """Split a line's value into delivered and returned parts, penny-safe.

    The returned part is rounded, and the delivered part takes the remainder
    so that delivery_net_val + return_net_val always equals net_val exactly.
    """
    if quantity == 0:
        return ZERO, ZERO
    return_net_val = (net_val * return_quantity / quantity).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    delivery_net_val = net_val - return_net_val
    return delivery_net_val, return_net_val


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("", response_model=APIResponse[dict])
async def save_delivery(
    payload: DeliverySaveRequest,
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Save a customer's entire delivery for a date in one atomic operation.

    The app reports quantities only; all money values are computed here.
    Every assigned invoice for the customer must be present, none may be
    already delivered, and each line's delivery/return split must add up to
    the assigned quantity. Any failure aborts the whole save.
    """
    now = datetime.now(timezone.utc)

    # --- Load all of this customer's invoices for the date ------------------
    stmt = (
        select(RdlDeliveryCollection)
        .options(selectinload(RdlDeliveryCollection.items))
        .where(
            RdlDeliveryCollection.da_code == current_da.da_code,
            RdlDeliveryCollection.customer_id == payload.customer_id,
            RdlDeliveryCollection.billing_date == payload.billing_date,
        )
    )
    db_invoices = (await db.execute(stmt)).scalars().all()

    if not db_invoices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assignment found for this customer on the given date",
        )

    db_by_doc = {inv.billing_doc_no: inv for inv in db_invoices}
    payload_docs = {inv.billing_doc_no for inv in payload.invoices}

    # --- Gate 1: the payload must cover exactly the assigned invoices -------
    assigned_docs = set(db_by_doc)
    if payload_docs != assigned_docs:
        missing = assigned_docs - payload_docs
        unknown = payload_docs - assigned_docs
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "All assigned invoices must be delivered together. "
                f"Missing: {sorted(missing)}. Unknown: {sorted(unknown)}."
            ),
        )

    # --- Gate 2: none already delivered (duplicate protection) --------------
    already = [inv.billing_doc_no for inv in db_invoices if inv.delivery_status]
    if already:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Already delivered: {sorted(already)}",
        )

    # --- Validate and stage every line before writing anything --------------
    # Nothing is mutated until all checks pass, so a later failure leaves the
    # session clean for rollback.
    for inv_input in payload.invoices:
        db_invoice = db_by_doc[inv_input.billing_doc_no]
        db_items_by_key = {
            (item.material_id, item.batch): item for item in db_invoice.items
        }

        # Gate 3: payload items must match the invoice's items exactly
        payload_keys = {(i.material_id, i.batch) for i in inv_input.items}
        if payload_keys != set(db_items_by_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Item mismatch for invoice {inv_input.billing_doc_no}. "
                    "Every line of the invoice must be sent."
                ),
            )
        
        # Gate 5: an invoice with any returned line needs one reason
        has_return = any(i.return_quantity > 0 for i in inv_input.items)
        if has_return and not inv_input.return_reason_code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail = (
                    "return_reason_code is required for invoice "
                    f"{inv_input.billing_doc_no} because it has returned items."
                ),
            )

        return_total = ZERO
        for item_input in inv_input.items:
            db_item = db_items_by_key[(item_input.material_id, item_input.batch)]

            # Gate 4: delivery + return must equal the assigned quantity
            if (
                item_input.delivery_quantity + item_input.return_quantity
                != db_item.quantity
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=(
                        f"Quantity mismatch for material {item_input.material_id} "
                        f"in invoice {inv_input.billing_doc_no}: delivered "
                        f"{item_input.delivery_quantity} + returned "
                        f"{item_input.return_quantity} must equal {db_item.quantity}",
                    ),
                )

            # Compute money from the stored net_val (never from the client)
            return_qty = db_item.quantity - item_input.delivery_quantity
            delivery_net_val, return_net_val = _split_value(
                db_item.net_val, db_item.quantity, return_qty
            )

            db_item.delivery_quantity = item_input.delivery_quantity
            db_item.return_quantity = return_qty
            db_item.delivery_net_val = delivery_net_val
            db_item.return_net_val = return_net_val

            return_total += return_net_val

        # --- Update the invoice header ------------------------------------
        db_invoice.return_value = return_total
        db_invoice.return_status = return_total > ZERO
        # Keep a reason only when something was actually returned
        db_invoice.return_reason_code = (
            inv_input.return_reason_code if has_return else None
        )
        if return_total == ZERO:
            db_invoice.return_type = None
        elif return_total >= db_invoice.invoice_value:
            db_invoice.return_type = "F"  # full return
        else:
            db_invoice.return_type = "P"  # partial return
        db_invoice.delivery_status = True
        db_invoice.delivery_datetime = now
        db_invoice.delivery_latitude = payload.latitude
        db_invoice.delivery_longitude = payload.longitude

        # Whatever was delivered is now due until it is collected
        db_invoice.due_value = db_invoice.invoice_value - return_total
        db_invoice.due_status = db_invoice.due_value > ZERO

    # --- One commit: all invoices saved together or none --------------------
    await db.commit()

    return APIResponse(
        message=f"Delivery saved for {len(payload.invoices)} invoice(s)",
        data={"customer_id": payload.customer_id, "invoice_count": len(payload.invoices)},
    )