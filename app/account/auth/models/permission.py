"""Module containing model definitions for Permission."""

from sqlalchemy.orm import Mapped, mapped_column

from toolkit.database.annotations import str64, text
from toolkit.database.mixins import CommonMixin
from toolkit.database.orm import Base


class Permission(CommonMixin, Base):
    """Model class representing permissions."""

    __tablename__ = "account__auth__permission"

    # Columns
    name: Mapped[str64] = mapped_column(
        nullable=False,
        unique=True,
        comment="Permission name (e.g., read, write, delete)",
    )
    description: Mapped[text] = mapped_column(
        nullable=False,
        comment="Description of the permission",
    )

    def __str__(self) -> str:
        """Return a string representation of the Permission object."""
        return f"<Permission(name={self.name}, description={self.description})>"

    def __repr__(self) -> str:
        """Return a human-readable string representation of the Permission object."""
        return f"Permission(name={self.name}, description={self.description})"
