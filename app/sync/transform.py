import psycopg2

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("transform", category="sync")

def _log_skipped(cur, billing_date: str | None) -> int:
    date_filter = "s.billing_date = %s" if billing_date else ""
    params = (billing_date,) if billing_date else ()

    where_parts = ["(c.customer_id IS NULL OR u.da_code IS NULL)"]
    if date_filter:
        where_parts.append(date_filter)
    where_clause = "WHERE " + " AND ".join(where_parts)

    skip_sql = f"""
        SELECT DISTINCT s.billing_doc_no, s.customer_id, LTRIM(d.da_code, '0'),
            CASE WHEN c.customer_id IS NULL THEN 'customer_missing'
                 ELSE 'da_missing' END
        FROM rpl_sales_info_sap s
        JOIN rdl_delivery_info_sap d ON s.billing_doc_no = d.billing_doc_no
        LEFT JOIN rpl_customer_list c ON s.customer_id = c.customer_id
        LEFT JOIN rdl_user_list u ON LTRIM(d.da_code, '0') = u.da_code
        {where_clause} 
    """
    cur.execute(skip_sql, params)
    skipped = cur.fetchall()

    if skipped:
        from psycopg2.extras import execute_values
        insert_sql = """
            INSERT INTO rdl_transform_skip
                (billing_doc_no, customer_id, da_code, reason, sync_date, resolved)
            VALUES %s 
            ON CONFLICT (billing_doc_no, sync_date) DO NOTHING
        """
        rows = [(bd, cust, da, reason, billing_date, False) for bd, cust, da, reason in skipped]
        execute_values(cur, insert_sql, rows)

        for bd, cust, da, reason in skipped:
            logger.warning(f"Transform skip: invoice={bd} reason={reason}")

    return len(skipped)


def transform_deliveries(billing_date: str | None = None) -> dict:
    """rpl_sales_info_sap (raw line) → rdl_delivery_collection (header) + 
    rdl_delivery_return_item (line)। DA-assigned invoice-i (INNER JOIN)।"""

    conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    conn.autocommit = False

    date_filter = "WHERE s.billing_date = %s" if billing_date else ""
    params = (billing_date,) if billing_date else ()

    try:
        with conn.cursor() as cur:
            skipped_count = _log_skipped(cur, billing_date)
            
            # --- 1. HEADER: rdl_delivery_collection ---
            header_sql = f"""
                INSERT INTO rdl_delivery_collection (
                    billing_doc_no, gate_pass_no, billing_date, customer_id, da_code,
                    billing_type, plant, sales_type, sales_org, delv_no, vehicle_no,
                    company_code, assignment, reference, item_category,
                    invoice_value,
                    delivery_status, cash_collection_status, return_status, due_status
                )
                SELECT
                    s.billing_doc_no,
                    MAX(s.gate_pass_no),
                    MAX(s.billing_date),
                    MAX(s.customer_id),
                    MAX(LTRIM(d.da_code, '0')),
                    MAX(s.billing_type),
                    MAX(s.plant),
                    MAX(s.sales_type),
                    MAX(s.sales_org),
                    MAX(d.delv_no),
                    MAX(d.vehicle_no),
                    MAX(s.company_code),
                    MAX(s.assignment),
                    MAX(s.reference),
                    MAX(s.item_category),
                    SUM(s.net_val),
                    false, false, false, false
                FROM rpl_sales_info_sap s
                JOIN rdl_delivery_info_sap d ON s.billing_doc_no = d.billing_doc_no
                JOIN rpl_customer_list c ON s.customer_id = c.customer_id
                JOIN rdl_user_list u ON LTRIM(d.da_code, '0') = u.da_code
                {date_filter}
                GROUP BY s.billing_doc_no
                ON CONFLICT (billing_doc_no) DO NOTHING
            """
            cur.execute(header_sql, params)
            header_count = cur.rowcount

            # --- 2. ITEM: rdl_delivery_return_item ---
            item_sql = f"""
                INSERT INTO rdl_delivery_return_item (
                    billing_doc_no, material_id, batch, team, quantity,
                    tp, vat, net_val,
                    delivery_quantity, return_quantity, delivery_net_val, return_net_val
                )
                SELECT
                    s.billing_doc_no, s.material_id, s.batch, s.team, s.quantity,
                    s.tp, s.vat, s.net_val,
                    0, 0, 0, 0
                FROM rpl_sales_info_sap s
                JOIN rdl_delivery_info_sap d ON s.billing_doc_no = d.billing_doc_no
                JOIN rpl_customer_list c ON s.customer_id = c.customer_id
                JOIN rdl_user_list u ON LTRIM(d.da_code, '0') = u.da_code
                {date_filter}
                ON CONFLICT (billing_doc_no, material_id, batch) DO NOTHING
            """
            cur.execute(item_sql, params)
            item_count = cur.rowcount

        conn.commit()
        return {"headers": header_count, "items": item_count, "skipped": skipped_count}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()