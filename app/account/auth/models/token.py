"""Module containing model definitions for Token."""

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.database.annotations import str255
from config.database.orm import Base
from toolkit.database.mixins import CommonMixin


class Token(CommonMixin, Base):
    """Model representing..."""

    __tablename__ = "account__auth__token"

    # Columns
    user_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__user.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing users table",
    )
    refresh_token: Mapped[str255] = mapped_column(
        nullable=False,
        unique=True,
        comment="Refresh token for the user",
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
        comment="Expiration time of the refresh token",
    )

    def __str__(self) -> str:
        """Return a string representation of the Token object."""
        return f"<Token(user_id={self.user_id}, expires_at={self.expires_at})>"

    def __repr__(self) -> str:
        """Return a human-readable string representation of the Token object."""
        return f"Token(user_id={self.user_id}, expires_at={self.expires_at})"
