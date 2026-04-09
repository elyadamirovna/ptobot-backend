"""add company_name to users"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0004_user_company"
down_revision = "0003_sites_report_fk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("company_name", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "company_name")
