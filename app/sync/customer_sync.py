import psycopg2
from datetime import date 
from app.core.config import settings
from app.sync.base_sync import bulk_upsert, unique_fetch_from_sap




CUSTOMER_COLUMN_MAP = {
    "PARTNER": "customer_id",
    "Name1": "name1",
    "Name2": "name2",
    "ContactPerson": "customer_name",
    "MobileNo": "mobile_no",
    "Email": "email",
    "Street": "street",
    "Street1": "street1",
    "Street2": "street2",
    "Street3": "street3",
    "PostCode": "post_code",
    "Upazilla": "upazila",
    "District": "district",
    "DrugRegNo": "drug_reg_no",
    "CustomerGrp": "customer_group",
    "TransPZone": "trans_p_zone",
}

TARGET_COLUMNS = [
    "customer_id", "shop_name", "customer_name", "mobile_no", "email",
    "street", "post_code", "upazila", "district", "drug_reg_no",
    "customer_group", "route_code", "active",
]
CONFLICT_COLUMNS = ["customer_id"]


def _clean(row: dict) -> dict:
    # shop_name = Name1 + Name2 (khali bad)
    names = [row.pop("name1", None), row.pop("name2", None)]
    row["shop_name"] = " ".join(n.strip() for n in names if n and n.strip())

    # street = 4 ta street jor (khali bad)
    parts = [row.pop("street", None), row.pop("street1", None),
             row.pop("street2", None), row.pop("street3", None)]
    row["street"] = ", ".join(p.strip() for p in parts if p and p.strip())

    # route_code = TransPZone theke samne-r 0 bad
    tpz = row.pop("trans_p_zone", None)
    row["route_code"] = tpz.strip().lstrip("0") if tpz and tpz.strip() else None

    # active — raw SQL-e default kaj kore na, explicit
    row["active"] = True
    return row


def _load_valid_routes() -> set[str]:
    """Amader rdl_route_list-er sob route_code ekta set-e (druto check-er jonn)."""
    conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT route_code FROM rdl_route_list")
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()
        
def _save_rejects(rejected: list[dict], sync_date: str) -> None:
    """Route-missing customer-der rdl_customer_sync_reject-e boshai (admin-er jonn)।"""
    if not rejected:
        return

    import psycopg2
    from psycopg2.extras import execute_values
    from app.core.config import settings

    conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    try:
        rows = [
            (r["customer_id"], r["route_code"], r.get("shop_name"),
             "route_missing", sync_date, False)
            for r in rejected
        ]

        with conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO rdl_customer_sync_reject "
                "(customer_id, route_code, shop_name, reason, sync_date, resolved) VALUES %s"
                "ON CONFLICT (customer_id, sync_date) DO NOTHING",
                rows,
            )
        conn.commit()
    finally:
        conn.close()


def sync_customer(sync_date: str | None = None):
    if sync_date is None:
        sync_date = date.today().isoformat()
        
    valid_routes = _load_valid_routes()
    valid_rows = []
    rejected = []   # route missing — admin-ke janate hobe

    for row in unique_fetch_from_sap(sap_table="Customer", column_map=CUSTOMER_COLUMN_MAP):
        clean = _clean(row)
        if clean["route_code"] in valid_routes:
            valid_rows.append(clean)
        else:
            rejected.append({
                "customer_id": clean["customer_id"],
                "route_code": clean["route_code"],
                "shop_name": clean.get("shop_name"),
            })

    # valid-gulo bulk insert
    inserted = bulk_upsert(
        target_table="rpl_customer_list",
        target_columns=TARGET_COLUMNS,
        conflict_columns=CONFLICT_COLUMNS,
        rows=valid_rows,   # already _clean kora, kintu bulk_upsert abar transform korbe na (transform=None)
    )
    
    _save_rejects(rejected, sync_date)

    return inserted, len(rejected)