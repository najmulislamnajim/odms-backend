# FastAPI Imports
from fastapi import APIRouter, Depends

# SQLAlchemy Imports
from sqlalchemy.ext.asyncio import AsyncSession

# App Imports
from app.api.deps import get_current_da
from app.db.session import get_db
from app.models.user import RdlUserList
from app.schemas.delivery import DeliverySaveRequest
from app.schemas.response import APIResponse
from app.services.delivery import delivery_service

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.post("", response_model=APIResponse[dict])
async def save_delivery(
    payload: DeliverySaveRequest,
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Save a customer's entire delivery for a date in one atomic operation."""
    result = await delivery_service.save_delivery(db, current_da.da_code, payload)
    return APIResponse(
        message=f"Delivery saved for {result.invoice_count} invoice(s)",
        data={"customer_id": result.customer_id, "invoice_count": result.invoice_count},
    )