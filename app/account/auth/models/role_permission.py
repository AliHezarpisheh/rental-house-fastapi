"""Module containing model definitions for RolePermission."""

from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from toolkit.database.mixins import IdMixin
from toolkit.database.orm import Base


class RolePermission(IdMixin, Base):
    """Model class representing the association between roles and permissions."""

    # Table Configurations
    __tablename__ = "account__auth__role_permission"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    # Columns
    role_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__role.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing roles table",
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__permission.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing permissions table",
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the record was created",
    )

    def __str__(self) -> str:
        """Return a string representation of the RolePermission object."""
        return (
            f"<RolePermission(role_id={self.role_id}, "
            f"permission_id={self.permission_id})>"
        )

    def __repr__(self) -> str:
        """Return a human-readable string representation of the RolePermission obj."""
        return (
            f"RolePermission(role_id={self.role_id}, "
            f"permission_id={self.permission_id})"
        )
