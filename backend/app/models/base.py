from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Column, DateTime, MetaData, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from app.core.config import settings


metadata = MetaData(schema=settings.database_schema)
SCHEMA_PREFIX = f"{metadata.schema}." if metadata.schema else ""

Base = declarative_base(metadata=metadata)


class UUIDPrimaryKeyMixin:
    """Reusable UUID primary key definition."""

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
        default=uuid4,
    )


class TimestampMixin:
    """Reusable timestamp columns for auditing."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


__all__ = ["Base", "UUIDPrimaryKeyMixin", "TimestampMixin", "SCHEMA_PREFIX"]


