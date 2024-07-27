"""Module containing model definitions for Role."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database.annotations import str64, text
from config.database.orm import Base
from toolkit.database.mixins import CommonMixin

if TYPE_CHECKING:
    from .permission import Permission
else:
    Permission = "Permission"


class Role(CommonMixin, Base):
    """Model class representing user roles."""

    __tablename__ = "account__auth__role"

    # Columns
    name: Mapped[str64] = mapped_column(
        nullable=False, unique=True, comment="Role name (e.g., admin, user, moderator)"
    )
    description: Mapped[text] = mapped_column(
        nullable=False,
        comment="Description of the role",
    )

    # Relationships
    permissions: Mapped[list[Permission]] = relationship(
        secondary="account__auth__role_permission",
        backref="roles",
    )

    def __str__(self) -> str:
        """Return a string representation of the Role object."""
        return f"<Role(name={self.name}, description={self.description})>"

    def __repr__(self) -> str:
        """Return a human-readable string representation of the Role object."""
        return f"Role(name={self.name}, description={self.description})"
