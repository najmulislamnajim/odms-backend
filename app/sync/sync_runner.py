from datetime import datetime, date 

import psycopg2

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("runner", category="sync")


def _log_failure(sync_type: str, sync_date: str | None, error: str, started: datetime, ended: datetime) -> None:
    try:
        conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO rdl_sync_log (sync_type, status, sync_date, error_message, started_at, ended_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (sync_type, "failed", sync_date, error, started, ended),
            )
        conn.commit()
        conn.close()
    except Exception:
        logger.exception("Failed to write sync_log")


def run_sync(sync_type: str, sync_fn, sync_date: str | None = None):
    started = datetime.now()
    logger.info(f"{sync_type} sync shuru (date={sync_date})")

    try:
        result = sync_fn()
        logger.info(f"{sync_type} sync shesh: {result}")
        return result
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error(f"{sync_type} sync FAIL: {error_msg}")
        ended = datetime.now()
        _log_failure(sync_type, sync_date, error_msg, started, ended)
        raise 
    
    
def run_all_syncs(sync_date: str | None = None):
    if sync_date is None:
        sync_date = date.today().isoformat()

    from app.sync.material_sync import sync_material
    from app.sync.customer_sync import sync_customer
    from app.sync.sales_sync import sync_sales_info
    from app.sync.delivery_info_sync import sync_delivery_info
    from app.sync.transform import transform_deliveries

    results = {}

    results["material"] = run_sync("material", sync_material)

    results["customer"] = run_sync("customer", lambda: sync_customer(sync_date), sync_date)

    results["sales"] = run_sync("sales", lambda: sync_sales_info(sync_date), sync_date)
    results["delivery_info"] = run_sync("delivery_info", lambda: sync_delivery_info(sync_date), sync_date)
    
    results["transform"] = run_sync("transform", lambda: transform_deliveries(sync_date), sync_date)

    return results