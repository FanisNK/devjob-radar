from datetime import datetime

from sqlalchemy import (
  DateTime,
  ForeignKey,
  Integer,
  String,
  Text,
  UniqueConstraint,
  func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Application(Base):
  __tablename__ = "applications"

  __table_args__ = (
    UniqueConstraint(
      "user_id",
      "job_id",
      name="uq_user_job_application",
    ),
  )

  id: Mapped[int] = mapped_column(
    Integer,
    primary_key=True,
    index=True,
  )

  user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id"),
    nullable=False,
  )

  job_id: Mapped[int] = mapped_column(
    ForeignKey("jobs.id"),
    nullable=False,
  )

  status: Mapped[str] = mapped_column(
    String(50),
    default="applied",
    nullable=False,
  )

  notes: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
  )

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )

  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )
