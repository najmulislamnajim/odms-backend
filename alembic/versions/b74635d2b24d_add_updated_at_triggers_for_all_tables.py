"""add updated_at triggers for all tables

Revision ID: b74635d2b24d
Revises: 69c3513345fd
Create Date: 2026-07-15 12:08:09.247418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b74635d2b24d'
down_revision: Union[str, Sequence[str], None] = '69c3513345fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # function ekbar (or replace = age thakle badle dao, na thakle banao)
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # jei table-gulote updated_at ache, tader talika
    tables = [
        "rdl_depot_list",
        "rdl_route_list",
        "rdl_route_depot_history",
        "rdl_user_list",
        "rdl_user_depot_history",
        "rdl_user_credential",
        "rpl_customer_list",
        "rpl_customer_sales_org",
        "rpl_customer_territory",
        "rpl_customer_route_history",
        "rdl_customer_location",
        "rpl_material_list",
        "rpl_user_list",
        "rpl_sales_info_sap",
        "rdl_delivery_info_sap",
        "rdl_delivery_collection",
        "rdl_delivery_return_item",
        "rdl_attendance",
        "rdl_conveyance",
        "rdl_customer_visit",
        "rdl_overdue",
        "rdl_payment_history",
    ]

    for table in tables:
        op.execute(f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION set_updated_at();
        """)


def downgrade() -> None:
    tables = [
        "rdl_depot_list",
        "rdl_route_list",
        "rdl_route_depot_history",
        "rdl_user_list",
        "rdl_user_depot_history",
        "rdl_user_credential",
        "rpl_customer_list",
        "rpl_customer_sales_org",
        "rpl_customer_territory",
        "rpl_customer_route_history",
        "rdl_customer_location",
        "rpl_material_list",
        "rpl_user_list",
        "rpl_sales_info_sap",
        "rdl_delivery_info_sap",
        "rdl_delivery_collection",
        "rdl_delivery_return_item",
        "rdl_attendance",
        "rdl_conveyance",
        "rdl_customer_visit",
        "rdl_overdue",
        "rdl_payment_history",
    ]
    for table in tables:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")