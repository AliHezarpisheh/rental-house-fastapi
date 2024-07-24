"""Module containing model definitions for Profile."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database.annotations import str255, text
from config.database.orm import Base
from toolkit.database.mixins import CommonMixin

if TYPE_CHECKING:
    from app.account.auth.models.user import User  # pragma: no cover
else:
    User = "User"


class Profile(CommonMixin, Base):
    """Model class representing user profile information."""

    __tablename__ = "account__auth__profile"

    # Columns
    full_name: Mapped[str255] = mapped_column(
        nullable=False,
        comment="Full name of the user.",
    )
    bio: Mapped[text | None] = mapped_column(
        nullable=True,
        comment="Short biography of the user.",
    )
    avatar_url: Mapped[str255 | None] = mapped_column(
        nullable=True,
        comment="URL to the user's avatar.",
    )
    location: Mapped[str255 | None] = mapped_column(
        nullable=True,
        comment="Location of the user.",
    )
    birthdate: Mapped[date | None] = mapped_column(
        nullable=True, comment="Birthdate of the user."
    )

    # Relationships
    user_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__user.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing users table",
    )
    user: Mapped[User] = relationship("User", backref="profile")

    def __str__(self) -> str:
        """Return a string representation of the Profile object."""
        return f"<Profile(full_name={self.full_name}, user_id={self.user_id})>"

    def __repr__(self) -> str:
        """Return a human-readable string representation of the Profile object."""
        return f"Profile(full_name={self.full_name}, user_id={self.user_id})"
