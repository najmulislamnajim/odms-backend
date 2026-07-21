import csv

import psycopg2
from psycopg2.extras import execute_values

from app.core.config import settings


def seed():
    conn = psycopg2.connect(settings.sync_database_url.replace("+psycopg2", ""))
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            # --- 1. Depot age (parent) ---
            with open("data/unique_depots.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                depots = [(r["depot_code"], r["depot_name"], True) for r in reader]
                

            execute_values(
                cur,
                "INSERT INTO rdl_depot_list (depot_code, depot_name, active) VALUES %s "
                "ON CONFLICT (depot_code) DO NOTHING",
                depots,
            )
            print(f"Depot: {len(depots)} row process holo")

            # --- 2. Route pore (child, depot_code FK) ---
            # amader route table-e depot_code lage, kintu unique_routes.csv-te depot nei!
            # tai mul CSV theke route→depot mapping banate hobe
            route_depot = {}
            with open("data/rdl_route_wise_depot.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    route_depot[r["route_code"]] = r["depot_code"]

            with open("data/unique_routes.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                routes = []
                for r in reader:
                    code = r["route_code"]
                    routes.append((code, r["route_name"], route_depot.get(code), True))

            execute_values(
                cur,
                "INSERT INTO rdl_route_list (route_code, route_name, depot_code, active) VALUES %s "
                "ON CONFLICT (route_code) DO NOTHING",
                routes,
            )
            print(f"Route: {len(routes)} row process holo")

        conn.commit()
        print("Seed complete!")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed()