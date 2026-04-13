"""add dashboard fields to sites

Revision ID: 0006_site_dashboard_fields
Revises: 0005_site_pto_engineer
Create Date: 2026-04-13
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0006_site_dashboard_fields"
down_revision = "0005_site_pto_engineer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sites", sa.Column("customer_name", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("project_manager_name", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("pto_responsible_name", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("sites", sa.Column("planned_end_date", sa.Date(), nullable=True))
    op.add_column("sites", sa.Column("budget_total", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("budget_spent", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("progress_percent", sa.Integer(), nullable=True))
    op.add_column("sites", sa.Column("status_note", sa.String(length=2000), nullable=True))


def downgrade() -> None:
    op.drop_column("sites", "status_note")
    op.drop_column("sites", "progress_percent")
    op.drop_column("sites", "budget_spent")
    op.drop_column("sites", "budget_total")
    op.drop_column("sites", "planned_end_date")
    op.drop_column("sites", "start_date")
    op.drop_column("sites", "pto_responsible_name")
    op.drop_column("sites", "project_manager_name")
    op.drop_column("sites", "customer_name")
