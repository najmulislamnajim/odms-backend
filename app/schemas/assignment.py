# Python Imports
from datetime import date
from decimal import Decimal
from enum import Enum

# Pydantic Imports
from pydantic import BaseModel


class AssignmentFilter(str, Enum):
    """Filter options for a DA's customer assignment list."""
    ALL = "all"
    DELIVERY_DONE = "delivery_done"
    COLLECTION_DONE = "collection_done"
    DELIVERY_PENDING = "delivery_pending"
    COLLECTION_PENDING = "collection_pending"


class CustomerSummary(BaseModel):
    """Per-customer summary of a DA's assigned invoices for a given date."""
    customer_id: str
    shop_name: str | None
    address: str | None
    invoice_count: int
    total_amount: Decimal
    delivered_amount: Decimal
    collected_amount: Decimal
    return_amount: Decimal
    # overdue: Decimal
    status: str | None 
    
class CustomerInfo(BaseModel):
    """Customer profile shown at the top of the detail screen."""
    customer_id: str 
    shop_name: str | None 
    address: str | None 
    mobile_no: str | None 
    # overdue: Decimal 
    
class MaterialItem(BaseModel):
    """A product line of an invoice with its delivery and return state."""
    material_id: str 
    material_name: str | None 
    batch: str | None 
    quantity: int 
    net_val: Decimal
    delivery_quantity: int 
    delivery_net_val: Decimal 
    return_quantity: int 
    return_net_val: Decimal 
    return_reason_code: str | None 
    
class InvoiceDetail(BaseModel):
    "An invoice with its product lines and delivery/collection state."
    billing_doc_no: str 
    producer_company: str | None 
    invoice_value: Decimal 
    delivered_amount: Decimal 
    return_amount: Decimal 
    collected_amount: Decimal 
    delivery_status: bool 
    return_status: bool 
    collection_status: bool 
    return_type: str | None 
    materials: list[MaterialItem]
    
class AssignmentDetail(BaseModel): 
    """A DA's full assignment for one customer on a given date."""
    customer: CustomerInfo 
    billing_date: date 
    total_amount: Decimal 
    delivered_amount: Decimal 
    collected_amount: Decimal 
    # overdue: Decimal  
    invoices: list[InvoiceDetail]