"""Module containing model definitions for UserRole."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from config.database.orm import Base
from toolkit.database.mixins import IdMixin

if TYPE_CHECKING:
    from .role import Role  # pragma: no cover
    from .user import User  # pragma: no cover
else:
    User = "User"
    Role = "Role"


class UserRole(IdMixin, Base):
    """Model class representing the association between users and roles."""

    # Table Configurations
    __tablename__ = "account__auth__user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    # Columns
    user_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__user.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing users table",
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__role.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing roles table",
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the record was created",
    )

    def __str__(self) -> str:
        """Return a string representation of the UserRole object."""
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"

    def __repr__(self) -> str:
        """Return a human-readable string representation of the UserRole object."""
        return f"UserRole(user_id={self.user_id}, role_id={self.role_id})"
