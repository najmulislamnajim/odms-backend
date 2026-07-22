# Python Imports
from decimal import Decimal
from datetime import date as date_type

# FastAPI Imports
from fastapi import APIRouter, Depends, Query, Path, status, HTTPException

# SQLAlchemy Imports
from sqlalchemy import Numeric, and_, case, cast, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.api.deps import get_current_da
from app.db.session import get_db
from app.models.customer import RplCustomerList
from app.models.delivery_collection import RdlDeliveryCollection
from app.models.delivery_return_item import RdlDeliveryReturnItem
from app.models.user import RdlUserList
from app.schemas.assignment import (
    AssignmentDetail,
    AssignmentFilter,
    CustomerInfo, 
    CustomerSummary,
    InvoiceDetail, 
    MaterialItem
)
from app.schemas.response import APIResponse

router = APIRouter(prefix="/assignments", tags=["assignments"])

ZERO = Decimal("0.00")

# ----------------------------------------------------------------------------------------
# Helpers 
# ----------------------------------------------------------------------------------------

def _build_material_item(item: RdlDeliveryReturnItem) -> MaterialItem:
    """Map an invoice line to its API representation."""
    return MaterialItem(
        material_id=item.material_id, 
        material_name=item.material.material_name if item.material else None, 
        batch = item.batch, 
        quantity=item.quantity, 
        net_val=item.net_val,
        delivery_quantity=item.delivery_quantity, 
        delivery_net_val = item.delivery_net_val,
        return_quantity=item.return_quantity, 
        return_net_val=item.return_net_val,
        return_reason_code=item.return_reason_code,
    )
    
def _build_invoice_detail(invoice: RdlDeliveryCollection) -> InvoiceDetail:
    """Map an invoice and its lines to the API representation.
    
    An invoice always belongs to a single producer company, so the first line's company
    represents the whole invoice. 
    """
    return_amount = invoice.return_value or ZERO
    delivered_amount = (
        invoice.invoice_value - return_amount if invoice.delivery_status else ZERO
    )
    producer_company = next(
        (item.material.producer_company for item in invoice.items if item.material), 
        None,
    )
    
    return InvoiceDetail(
        billing_doc_no=invoice.billing_doc_no, 
        producer_company=producer_company,
        invoice_value=invoice.invoice_value, 
        delivered_amount=delivered_amount,
        return_amount=return_amount,
        collected_amount=invoice.cash_collection_value or ZERO, 
        delivery_status=invoice.delivery_status,
        collection_status = invoice.cash_collection_status,
        return_status=invoice.return_status,
        return_type=invoice.return_type,
        materials=[_build_material_item(item) for item in invoice.items]
    ) 
    
# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=APIResponse[list[CustomerSummary]])
async def list_assignments(
    billing_date: date_type | None = Query(None, description="Defaults to today"),
    filter: AssignmentFilter = Query(
        AssignmentFilter.ALL, description="Narrow the list by pending work"
    ), 
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
): 
    """List the DA's customers for  a date with delivery and collection totals"""
    target_date = billing_date or date_type.today()
    
    invoice = RdlDeliveryCollection 
    is_delivery_pending = invoice.delivery_status.is_(False)
    is_delivery_done = invoice.delivery_status.is_(True)
    is_collection_pending = and_(
        invoice.delivery_status.is_(True),
        invoice.cash_collection_status.is_(False)
    )
    is_collection_done = and_(
        invoice.delivery_status.is_(True),
        invoice.cash_collection_status.is_(True)
    )
    
    status_case = case(
        (
            func.count().filter(is_delivery_pending) > 0,
            "Delivery Pending"
        ),
        (
            func.count().filter(is_collection_pending) > 0,
            "Collection Pending"
        ),
        (
            func.count().filter(is_collection_done) == func.count(),
            "Collection Done"
        ),
        else_="Delivery Done"
    )
    
    # Delivered value counts only once the invoice is actually delivered.
    delivered_value = case(
        (
            invoice.delivery_status.is_(True),
            invoice.invoice_value - func.coalesce(invoice.return_value, 0),
        ), 
        else_=cast(0, Numeric(18,2)),
    )
    
    stmt = (
        select(
            RplCustomerList.customer_id,
            RplCustomerList.shop_name, 
            RplCustomerList.street.label("address"),
            func.count().label("invoice_count"),
            func.sum(invoice.invoice_value).label("total_amount"),
            func.sum(delivered_value).label("delivered_amount"),
            func.sum(func.coalesce(invoice.cash_collection_value, 0)).label(
                "collected_amount",
            ),
            func.sum(func.coalesce(invoice.return_value, 0)).label(
                "return_amount",
            ),
            func.count().filter(is_delivery_pending).label("pending_delivery_count"),
            func.count().filter(is_collection_pending).label(
                "pending_collection_count"
            ),
            status_case.label("status")
        )
        .join(RplCustomerList, invoice.customer_id == RplCustomerList.customer_id)
        .where(
            invoice.da_code == current_da.da_code,
            invoice.billing_date == target_date,
        )
        .group_by(
            RplCustomerList.customer_id,
            RplCustomerList.shop_name,
            RplCustomerList.street,
        )
        .order_by(RplCustomerList.shop_name)
    )
    
    # Filters compare aggregates, so they belong in HAVING rather than WHERE. 
    if filter is AssignmentFilter.DELIVERY_PENDING:
        stmt = stmt.having(func.count().filter(is_delivery_pending) > 0)
    elif filter is AssignmentFilter.DELIVERY_DONE:
        stmt = stmt.having(func.count().filter(is_delivery_done) > 0)
    elif filter is AssignmentFilter.COLLECTION_PENDING:
        stmt = stmt.having(func.count().filter(is_collection_pending) > 0)
    elif filter is AssignmentFilter.COLLECTION_DONE:
        stmt = stmt.having(func.count().filter(is_collection_done) > 0)
        
    rows = (await db.execute(stmt)).all()
    customers = [CustomerSummary(**row._mapping) for row in rows]
    
    return APIResponse(
        message=f"{len(customers)} customer(s) found.",
        data = customers,
    )