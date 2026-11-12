# Python Imports
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

# SQLAlchemy Imports
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# App Imports
from app.core.exceptions import (
    BadRequestError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
)
from app.models.delivery_collection import RdlDeliveryCollection
from app.schemas.delivery import DeliverySaveRequest
from app.services.delivery.delivery_logic import return_type_for, split_line_value

ZERO = Decimal("0.00")


@dataclass
class DeliveryResult:
    customer_id: str
    invoice_count: int


async def save_delivery(
    db: AsyncSession,
    da_code: str,
    payload: DeliverySaveRequest,
    now: datetime | None = None,
) -> DeliveryResult:
    """Save a customer's entire delivery for a date in one atomic operation.

    The app reports quantities only; all money values are computed here.
    Any failed check aborts the whole save.
    """
    now = now or datetime.now(timezone.utc)

    # Load all of this customer's invoices for the date
    stmt = (
        select(RdlDeliveryCollection)
        .options(selectinload(RdlDeliveryCollection.items))
        .where(
            RdlDeliveryCollection.da_code == da_code,
            RdlDeliveryCollection.customer_id == payload.customer_id,
            RdlDeliveryCollection.billing_date == payload.billing_date,
        )
    )
    db_invoices = (await db.execute(stmt)).scalars().all()
    if not db_invoices:
        raise NotFoundError("No assignment found for this customer on the given date")

    db_by_doc = {inv.billing_doc_no: inv for inv in db_invoices}

    # Gate 1: the payload must cover exactly the assigned invoices
    assigned_docs = set(db_by_doc)
    payload_docs = {inv.billing_doc_no for inv in payload.invoices}
    if payload_docs != assigned_docs:
        raise BadRequestError(
            "All assigned invoices must be delivered together. "
            f"Missing: {sorted(assigned_docs - payload_docs)}. "
            f"Unknown: {sorted(payload_docs - assigned_docs)}."
        )

    # Gate 2: none already delivered (duplicate protection)
    already = [inv.billing_doc_no for inv in db_invoices if inv.delivery_status]
    if already:
        raise ConflictError(f"Already delivered: {sorted(already)}")

    # Changes below stay in the session until commit. If any later gate
    # fails, nothing is committed and the session discards them.
    for inv_input in payload.invoices:
        db_invoice = db_by_doc[inv_input.billing_doc_no]
        db_items_by_key = {(i.material_id, i.batch): i for i in db_invoice.items}

        # Gate 3: payload items must match the invoice's items exactly
        payload_keys = {(i.material_id, i.batch) for i in inv_input.items}
        if payload_keys != set(db_items_by_key):
            raise BadRequestError(
                f"Item mismatch for invoice {inv_input.billing_doc_no}. "
                "Every line of the invoice must be sent."
            )

        # Gate 4: an invoice with any returned line needs one reason
        has_return = any(i.return_quantity > 0 for i in inv_input.items)
        if has_return and not inv_input.return_reason_code:
            raise BusinessRuleError(
                "return_reason_code is required for invoice "
                f"{inv_input.billing_doc_no} because it has returned items."
            )

        return_total = ZERO
        for item_input in inv_input.items:
            db_item = db_items_by_key[(item_input.material_id, item_input.batch)]

            # Gate 5: delivery + return must equal the assigned quantity
            if item_input.delivery_quantity + item_input.return_quantity != db_item.quantity:
                raise BusinessRuleError(
                    f"Quantity mismatch for material {item_input.material_id} "
                    f"in invoice {inv_input.billing_doc_no}: delivered "
                    f"{item_input.delivery_quantity} + returned "
                    f"{item_input.return_quantity} must equal {db_item.quantity}"
                )

            # Money always comes from the stored net_val, never from the client
            delivery_net_val, return_net_val = split_line_value(
                db_item.net_val, db_item.quantity, item_input.return_quantity
            )
            db_item.delivery_quantity = item_input.delivery_quantity
            db_item.return_quantity = item_input.return_quantity
            db_item.delivery_net_val = delivery_net_val
            db_item.return_net_val = return_net_val
            return_total += return_net_val

        # Update the invoice header
        db_invoice.return_value = return_total
        db_invoice.return_status = return_total > ZERO
        db_invoice.return_type = return_type_for(return_total, db_invoice.invoice_value)
        db_invoice.return_reason_code = inv_input.return_reason_code if has_return else None
        db_invoice.delivery_status = True
        db_invoice.delivery_datetime = now
        db_invoice.delivery_latitude = payload.latitude
        db_invoice.delivery_longitude = payload.longitude

        # Whatever was delivered is now due until it is collected
        db_invoice.due_value = db_invoice.invoice_value - return_total
        db_invoice.due_status = db_invoice.due_value > ZERO

    await db.commit()
    return DeliveryResult(customer_id=payload.customer_id, invoice_count=len(payload.invoices))