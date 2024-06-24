"""Pagination utility for API responses."""

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """Model representing pagination details."""

    total_items: int = Field(..., ge=0, description="Total number of items available.")
    total_pages: int = Field(
        ...,
        ge=1,
        description="Total number of pages available based on items per page.",
    )
    current_page: int = Field(
        ..., ge=1, description="The current page number being viewed."
    )
