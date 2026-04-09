"""add sites and report site foreign keys"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_sites_report_fk"
down_revision = "0002_create_users_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sites",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column(
            "contractor_id",
            sa.String(length=64),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_sites_contractor_id", "sites", ["contractor_id"], unique=False)

    op.add_column("reports", sa.Column("site_id", sa.String(length=64), nullable=True))
    op.add_column("reports", sa.Column("report_date", sa.Date(), nullable=True))

    op.execute("UPDATE reports SET report_date = DATE(created_at)")

    op.alter_column("reports", "user_id", existing_type=sa.String(length=128), type_=sa.String(length=64), nullable=False)
    op.create_foreign_key("fk_reports_user_id_users", "reports", "users", ["user_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_reports_site_id_sites", "reports", "sites", ["site_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_reports_site_id", "reports", ["site_id"], unique=False)
    op.alter_column("reports", "report_date", nullable=False)


def downgrade() -> None:
    op.drop_index("ix_reports_site_id", table_name="reports")
    op.drop_constraint("fk_reports_site_id_sites", "reports", type_="foreignkey")
    op.drop_constraint("fk_reports_user_id_users", "reports", type_="foreignkey")
    op.alter_column("reports", "user_id", existing_type=sa.String(length=64), type_=sa.String(length=128), nullable=False)
    op.drop_column("reports", "report_date")
    op.drop_column("reports", "site_id")

    op.drop_index("ix_sites_contractor_id", table_name="sites")
    op.drop_table("sites")
