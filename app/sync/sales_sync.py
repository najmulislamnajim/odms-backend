from datetime import date

from app.sync.base_sync import bulk_upsert, fetch_from_sap

SALES_COLUMN_MAP = {
    "BillingDocNo": "billing_doc_no",
    "GatePassNo": "gate_pass_no",
    "BillingDate": "billing_date",
    "PARTNER": "customer_id",
    "MATNR": "material_id",
    "Batch": "batch",
    "Quantity": "quantity",
    "TP": "tp",
    "Vat": "vat",
    "NetVal": "net_val",
    "BillingType": "billing_type",
    "Plant": "plant",
    "SalesOrg": "sales_org",
    "SalesType": "sales_type",
    "Team": "team",
    "CompanyCode": "company_code",
    "Assigment": "assignment",
    "TerritoryCode": "territory_code",
    "Refrence": "reference",
    "OrderType": "order_type",
    "ItemCategory": "item_category",
    "Cancel": "cancel",
}

TARGET_COLUMNS = list(SALES_COLUMN_MAP.values())
CONFLICT_COLUMNS = ["billing_doc_no", "billing_date", "material_id", "batch"]


def _clean(row: dict) -> dict:
    """quantity Decimal → int (amader model Integer)."""
    row["quantity"] = int(row["quantity"]) if row["quantity"] is not None else 0
    return row


def sync_sales_info(billing_date: str | None = None) -> int:
    if billing_date is None:
        billing_date = date.today().isoformat()

    rows = fetch_from_sap(
        sap_table="SalesInfoSAP",
        column_map=SALES_COLUMN_MAP,
        where_clause="WHERE BillingDate = %s",
        params=(billing_date,),
    )
    return bulk_upsert(
        target_table="rpl_sales_info_sap",
        target_columns=TARGET_COLUMNS,
        conflict_columns=CONFLICT_COLUMNS,
        rows=rows,
        transform=_clean,
    )