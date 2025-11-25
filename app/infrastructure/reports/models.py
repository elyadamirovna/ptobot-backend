"""SQLAlchemy models for reports."""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ReportModel(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    work_type_id: Mapped[str] = mapped_column(String(64), ForeignKey("work_types.id", ondelete="RESTRICT"), index=True)
    description: Mapped[str] = mapped_column(String(2000), default="")
    people: Mapped[str] = mapped_column(String(256), default="")
    volume: Mapped[str] = mapped_column(String(256), default="")
    machines: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    photo_urls: Mapped[List[str]] = mapped_column(JSONB, default=list)
