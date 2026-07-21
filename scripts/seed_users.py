import csv

import psycopg2
from psycopg2.extras import execute_values

from app.core.config import settings


def _load_valid_depots() -> set[str]:
    conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT depot_code FROM rdl_depot_list")
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def seed_users():
    valid_depots = _load_valid_depots()

    valid_rows = []
    skipped = []

    with open("data/rdl_users_list.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            da_code = r["da_code"].strip()
            depot = r["depot_code"].strip()
            da_name = r["da_name"].strip()

            # test user skip (naam-e 'test', ba da_name ajob)
            if "test" in da_name.lower() or "test" in r["user_type"].lower():
                skipped.append((da_code, da_name, "test_user"))
                continue

            # depot na thakle ba invalid hole skip
            if depot not in valid_depots:
                skipped.append((da_code, da_name, "depot_missing"))
                continue

            # status 1/0 → active True/False
            active = r["status"].strip() == "1"

            valid_rows.append((
                da_code,
                da_name,
                r["mobile_no"].strip() or None,
                r["user_type"].strip() or None,
                r["designation"].strip() or None,
                depot,
                active,
            ))

    conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    try:
        sql = """
            INSERT INTO rdl_user_list
                (da_code, da_name, mobile_no, user_type, designation, depot_code, active)
            VALUES %s
            ON CONFLICT (da_code) DO NOTHING
        """
        with conn.cursor() as cur:
            execute_values(cur, sql, valid_rows)
        conn.commit()
    finally:
        conn.close()

    print(f"Inserted: {len(valid_rows)}, Skipped: {len(skipped)}")
    print("Skip reasons:")
    for da_code, name, reason in skipped:
        print(f"  {da_code} ({name}): {reason}")


if __name__ == "__main__":
    seed_users()