"""add pto engineer assignment to sites"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0005_site_pto_engineer"
down_revision = "0004_user_company"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sites", sa.Column("pto_engineer_id", sa.String(length=64), nullable=True))
    op.create_foreign_key(
        "fk_sites_pto_engineer_id_users",
        "sites",
        "users",
        ["pto_engineer_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_sites_pto_engineer_id", "sites", ["pto_engineer_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sites_pto_engineer_id", table_name="sites")
    op.drop_constraint("fk_sites_pto_engineer_id_users", "sites", type_="foreignkey")
    op.drop_column("sites", "pto_engineer_id")
