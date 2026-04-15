"""extend work types hierarchy metadata"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_extend_work_types_hierarchy"
down_revision = "0002_add_report_work_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("work_types", sa.Column("parent_id", sa.String(length=64), nullable=True))
    op.add_column("work_types", sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("work_types", sa.Column("unit", sa.String(length=32), nullable=True))
    op.add_column("work_types", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("work_types", sa.Column("requires_volume", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("work_types", sa.Column("requires_people", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("work_types", sa.Column("requires_machines", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_index("ix_work_types_parent_id", "work_types", ["parent_id"])
    op.create_foreign_key(
        "fk_work_types_parent_id",
        "work_types",
        "work_types",
        ["parent_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_work_types_parent_id", "work_types", type_="foreignkey")
    op.drop_index("ix_work_types_parent_id", table_name="work_types")
    op.drop_column("work_types", "requires_machines")
    op.drop_column("work_types", "requires_people")
    op.drop_column("work_types", "requires_volume")
    op.drop_column("work_types", "is_active")
    op.drop_column("work_types", "unit")
    op.drop_column("work_types", "sort_order")
    op.drop_column("work_types", "parent_id")
