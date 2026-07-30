# Python Imports
from datetime import date
from decimal import Decimal

# Pydantic Imports
from pydantic import BaseModel, Field


class PendingInvoice(BaseModel):
    """An invoice that has been delivered but not yet collected."""

    billing_doc_no: str
    billing_date: date
    invoice_value: Decimal
    due_value: Decimal


class CollectionRequest(BaseModel):
    """A customer-wise cash collection over one or more delivered invoices."""

    customer_id: str
    latitude: Decimal
    longitude: Decimal
    billing_doc_nos: list[str] = Field(min_length=1)