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
from app.schemas.assignment import AssignmentDetail, AssignmentFilter, CustomerSummary
from app.schemas.response import APIResponse
from app.services.delivery import assignment_service

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.get("", response_model=APIResponse[list[CustomerSummary]])
async def list_assignments(
    billing_date: date_type | None = Query(None, description="Defaults to today"),
    status_filter: AssignmentFilter = Query(
        AssignmentFilter.ALL, alias="filter", description="Narrow the list by pending work"
    ),
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """List the DA's customers for a date with delivery and collection totals."""
    customers = await assignment_service.list_customers(
        db, current_da.da_code, billing_date or date_type.today(), status_filter
    )
    return APIResponse(message=f"{len(customers)} customer(s) found.", data=customers)


@router.get("/{customer_id}", response_model=APIResponse[AssignmentDetail])
async def get_assignment_detail(
    customer_id: str = Path(..., description="Customer ID"),
    billing_date: date_type | None = Query(None, description="Defaults to today"),
    current_da: RdlUserList = Depends(get_current_da),
    db: AsyncSession = Depends(get_db),
):
    """Return one customer's invoices, product lines and current state."""
    detail = await assignment_service.get_detail(
        db, current_da.da_code, customer_id, billing_date or date_type.today()
    )
    return APIResponse(message="Assignment Detail.", data=detail)