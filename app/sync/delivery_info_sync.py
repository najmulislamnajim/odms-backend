from datetime import date 

from app.sync.base_sync import bulk_upsert, fetch_from_sap 

DELIVERY_INFO_COLUMN_MAP = {
    "BillingDocNo": "billing_doc_no",
    "BillingDate": "billing_date",
    "DelvNo": "delv_no",
    "VehicleNo": "vehicle_no",
    "DACode": "da_code",
    "DAName": "da_name",
    "Route": "route",
}

TARGET_COLUMNS = list(DELIVERY_INFO_COLUMN_MAP.values())
CONFLICT_COLUMNS = ["billing_doc_no"]

def sync_delivery_info(billing_date: str | None = None) -> int:
    if billing_date is None:
        billing_date = date.today().isoformat()

    rows = fetch_from_sap(
        sap_table="DeliveryInfoSAP",
        column_map=DELIVERY_INFO_COLUMN_MAP,
        where_clause="WHERE BillingDate = %s",
        params=(billing_date,),
    )
    return bulk_upsert(
        target_table="rdl_delivery_info_sap",
        target_columns=TARGET_COLUMNS,
        conflict_columns=CONFLICT_COLUMNS,
        rows=rows,
    )