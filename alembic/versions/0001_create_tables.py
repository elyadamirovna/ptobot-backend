"""create reports and work_types tables"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_create_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "work_types",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_work_types_name", "work_types", ["name"], unique=True)

    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("work_type_id", sa.String(length=64), sa.ForeignKey("work_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False, server_default=""),
        sa.Column("people", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("volume", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("machines", sa.String(length=256), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("photo_urls", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
    )
    op.create_index("ix_reports_user_id", "reports", ["user_id"])
    op.create_index("ix_reports_work_type_id", "reports", ["work_type_id"])


def downgrade() -> None:
    op.drop_index("ix_reports_work_type_id", table_name="reports")
    op.drop_index("ix_reports_user_id", table_name="reports")
    op.drop_table("reports")
    op.drop_index("ix_work_types_name", table_name="work_types")
    op.drop_table("work_types")
