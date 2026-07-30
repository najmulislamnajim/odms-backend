# Python Imports
from datetime import date
from decimal import Decimal

# Pydantic Imports
from pydantic import BaseModel, Field


class DeliveryItemInput(BaseModel):
    """One product line as reported by the app.

    Both delivery and return quantities are sent so the backend can
    cross-check them against the assigned quantity.
    """

    material_id: str
    batch: str
    delivery_quantity: int = Field(ge=0, description="Quantity actually delivered")
    return_quantity: int = Field(ge=0, description="Quantity returned")
    return_reason_code: str | None = Field(
        default=None, description="Required when return_quantity > 0"
    )


class DeliveryInvoiceInput(BaseModel):
    """One invoice with all of its product lines."""

    billing_doc_no: str
    items: list[DeliveryItemInput] = Field(min_length=1)


class DeliverySaveRequest(BaseModel):
    """A customer-wise delivery: every assigned invoice saved in one call."""

    customer_id: str
    billing_date: date
    latitude: Decimal
    longitude: Decimal
    invoices: list[DeliveryInvoiceInput] = Field(min_length=1)