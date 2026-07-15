import psycopg2
from datetime import date
from app.sync.sap_connection import get_sap_connection
from psycopg2.extras import execute_values

from app.core.config import settings

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

TARGET_COLUMNS = [
    "billing_doc_no", "gate_pass_no", "billing_date", "customer_id",
    "material_id", "batch", "quantity", "tp", "vat", "net_val",
    "billing_type", "plant", "sales_org", "sales_type", "team",
    "company_code", "assignment", "territory_code", "reference",
    "order_type", "item_category", "cancel",
]


def fetch_all_sales_info(billing_date: str):
    sap_columns = ", ".join(SALES_COLUMN_MAP.keys())
    query = f"SELECT {sap_columns} FROM SalesInfoSAP WHERE BillingDate = %s"
    with get_sap_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, (billing_date,))
        for row in cursor:
            yield {SALES_COLUMN_MAP[k]: v for k, v in row.items()}


def upsert_sales_info(billing_date: str | None = None, batch_size: int = 5000) -> int:
    if billing_date is None:
        billing_date = date.today().isoformat()
        
    pg_conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    pg_conn.autocommit = False
    total = 0

    cols = ", ".join(TARGET_COLUMNS)
    conflict_cols = "billing_doc_no, billing_date, material_id, batch"
    upsert_sql = (
        f"INSERT INTO rpl_sales_info_sap ({cols}) VALUES %s "
        f"ON CONFLICT ({conflict_cols}) DO NOTHING"
    )

    try:
        with pg_conn.cursor() as pg_cursor:
            batch = []
            for row in fetch_all_sales_info(billing_date):
                row["quantity"] = int(row["quantity"]) if row["quantity"] is not None else 0
                batch.append(tuple(row.get(c) for c in TARGET_COLUMNS))

                if len(batch) >= batch_size:
                    execute_values(pg_cursor, upsert_sql, batch)
                    total += len(batch)
                    batch = []

            if batch:
                execute_values(pg_cursor, upsert_sql, batch)
                total += len(batch)

        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        pg_conn.close()

    return total