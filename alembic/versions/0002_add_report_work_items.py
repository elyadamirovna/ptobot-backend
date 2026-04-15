"""add report work items table"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_add_report_work_items"
down_revision = "0001_create_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "report_work_items",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "report_id",
            sa.String(length=64),
            sa.ForeignKey("reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "work_type_id",
            sa.String(length=64),
            sa.ForeignKey("work_types.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=2000), nullable=False, server_default=""),
        sa.Column("people", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("volume", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("machines", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_report_work_items_report_id", "report_work_items", ["report_id"])
    op.create_index("ix_report_work_items_work_type_id", "report_work_items", ["work_type_id"])


def downgrade() -> None:
    op.drop_index("ix_report_work_items_work_type_id", table_name="report_work_items")
    op.drop_index("ix_report_work_items_report_id", table_name="report_work_items")
    op.drop_table("report_work_items")
