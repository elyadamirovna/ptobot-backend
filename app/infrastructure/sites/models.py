"""SQLAlchemy models for construction sites."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class SiteModel(Base):
    __tablename__ = "sites"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_manager_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pto_responsible_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget_total: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget_spent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    progress_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status_note: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    contractor_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    pto_engineer_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
