"""add updated_at trigger for route_wise_depot

Revision ID: 2ef5d89a1d88
Revises: cf3223746c33
Create Date: 2026-07-06 11:17:08.372682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ef5d89a1d88'
down_revision: Union[str, Sequence[str], None] = 'cf3223746c33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_route_wise_depot_updated_at
        BEFORE UPDATE ON rdl_route_wise_depot
        FOR EACH ROW
        EXECUTE FUNCTION set_updated_at();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_route_wise_depot_updated_at ON rdl_route_wise_depot;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")

