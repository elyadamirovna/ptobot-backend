"""SQLAlchemy models for work types."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class WorkTypeModel(Base):
    __tablename__ = "work_types"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("work_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_volume: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_people: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_machines: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
