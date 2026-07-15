import psycopg2
from psycopg2.extras import execute_values

from app.core.config import settings
from app.sync.sap_connection import get_sap_connection


def _execute_sap_query(query: str, column_map: dict, params: tuple = ()):
    """SAP-e query chালায়, protita row amader column-naam-e mapped kore dey।
    Connection kholা/bondho ekhane ek jaygায় (DRY)।"""
    with get_sap_connection() as conn:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(query, params)
        for row in cursor:
            yield {column_map[k]: v for k, v in row.items()}


def fetch_from_sap(sap_table: str, column_map: dict, where_clause: str = "", params: tuple = ()):
    """SAP theke ek table-er sob row ane (mapped)।"""
    sap_columns = ", ".join(column_map.keys())
    query = f"SELECT {sap_columns} FROM {sap_table} {where_clause}"
    yield from _execute_sap_query(query, column_map, params)


def unique_fetch_from_sap(sap_table: str, column_map: dict, where_clause: str = "", params: tuple = ()):
    """SAP theke DISTINCT (unique) row ane (mapped)। Ek entity onek bar thakle
    (jemon customer × sales_org), core field DISTINCT kore ek row dey।"""
    sap_columns = ", ".join(column_map.keys())
    query = f"SELECT DISTINCT {sap_columns} FROM {sap_table} {where_clause}"
    yield from _execute_sap_query(query, column_map, params)


def bulk_upsert(
    target_table: str,
    target_columns: list[str],
    conflict_columns: list[str],
    rows,
    transform=None,
    batch_size: int = 5000,
) -> int:
    """Amader PostgreSQL-e bulk upsert (ON CONFLICT DO NOTHING)।"""
    pg_conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    pg_conn.autocommit = False
    total = 0

    cols = ", ".join(target_columns)
    conflict = ", ".join(conflict_columns)
    sql = (
        f"INSERT INTO {target_table} ({cols}) VALUES %s "
        f"ON CONFLICT ({conflict}) DO NOTHING"
    )

    try:
        with pg_conn.cursor() as cur:
            batch = []
            for row in rows:
                if transform:
                    row = transform(row)
                batch.append(tuple(row.get(c) for c in target_columns))
                if len(batch) >= batch_size:
                    execute_values(cur, sql, batch)
                    total += len(batch)
                    batch = []
            if batch:
                execute_values(cur, sql, batch)
                total += len(batch)
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()
        raise
    finally:
        pg_conn.close()

    return total