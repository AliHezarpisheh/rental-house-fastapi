"""Defines mixins for API schema classes(Pydantic models)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.types import PositiveInt


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields (created_at and updated_at)."""

    created_at: datetime = Field(
        ...,
        description="The modification time of the object.",
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="The modification time of the object.",
    )


class AuditMixin(BaseModel):
    """Mixin for audit fields (created_by and updated_by)."""

    created_by: str = Field(
        ...,
        description="ID of the user who created the object.",
    )
    updated_by: Optional[str] = Field(
        None,
        description="ID of the user who modified the object.",
    )


class IdMixin(BaseModel):
    """Mixin for ID field (id)."""

    id: PositiveInt = Field(..., description="The unique identifier of the object.")


class CommonMixins(IdMixin, AuditMixin, TimestampMixin):
    """Combines common mixins: IdMixin, AuditMixin, and TimestampMixin."""
