# Python Imports
from datetime import date as date_type

# FastAPI Imports
from fastapi import APIRouter, Depends, Path, Query

# SQLAlchemy Imports
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.api.deps import get_current_da
from app.db.session import get_db
from app.models.user import RdlUserList
from app.schemas.collection import CollectionRequest, PendingInvoice
from app.schemas.response import APIResponse
from app.services.delivery import collection_service

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/pending/{customer_id}", response_model=APIResponse[list[PendingInvoice]])
async def list_pending_collections(
    customer_id: str = Path(..., description="Customer ID"),
    billing_date: date_type | None = Query(None, description="Defaults to today"),
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """List a customer's delivered-but-uncollected invoices for a date."""
    invoices = await collection_service.list_pending(
        db, current_da.da_code, customer_id, billing_date or date_type.today()
    )
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


@router.post("", response_model=APIResponse[dict])
async def collect_cash(
    payload: CollectionRequest,
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Collect cash across the selected invoices in one atomic operation."""
    result = await collection_service.collect_cash(db, current_da.da_code, payload)
    return APIResponse(
        message=f"Collected {result.collected_amount} from {result.invoice_count} invoice(s)",
        data={
            "customer_id": result.customer_id,
            "collected_amount": str(result.collected_amount),
            "round_down": str(result.round_down),
            "invoice_count": result.invoice_count,
        },
    )