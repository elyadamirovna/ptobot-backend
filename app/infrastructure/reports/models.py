"""SQLAlchemy models for reports."""
from __future__ import annotations

from datetime import date, datetime
from typing import List

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    site_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("sites.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    work_type_id: Mapped[str] = mapped_column(String(64), ForeignKey("work_types.id", ondelete="RESTRICT"), index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(String(2000), default="")
    people: Mapped[str] = mapped_column(String(256), default="")
    volume: Mapped[str] = mapped_column(String(256), default="")
    machines: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    photo_urls: Mapped[List[str]] = mapped_column(JSONB, default=list)
    work_items: Mapped[List["ReportWorkItemModel"]] = relationship(
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="ReportWorkItemModel.sort_order",
    )


class ReportWorkItemModel(Base):
    __tablename__ = "report_work_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    report_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("reports.id", ondelete="CASCADE"),
        index=True,
    )
    work_type_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("work_types.id", ondelete="RESTRICT"),
        index=True,
    )
    description: Mapped[str] = mapped_column(String(2000), default="")
    people: Mapped[str] = mapped_column(String(256), default="")
    volume: Mapped[str] = mapped_column(String(256), default="")
    machines: Mapped[str] = mapped_column(String(256), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    report: Mapped[ReportModel] = relationship(back_populates="work_items")
