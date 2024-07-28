"""Module containing model definitions for User."""

from typing import TYPE_CHECKING

from sqlalchemy import Index, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database.annotations import str255
from config.database.orm import Base
from toolkit.database.mixins import CommonMixin

if TYPE_CHECKING:
    from .activity_log import ActivityLog
    from .role import Role
    from .token import Token
else:
    Role = "Role"
    Token = "Token"
    ActivityLog = "ActivityLog"


class User(CommonMixin, Base):
    """Represents a user in the authentication system."""

    # Table Configurations
    __tablename__ = "account__auth__user"
    __table_args__ = (
        Index("ix_user_username", "username"),
        Index("ix_user_email", "email"),
    )

    # Columns
    username: Mapped[str255] = mapped_column(
        unique=True,
        nullable=False,
        comment="Unique username.",
    )
    email: Mapped[str255] = mapped_column(
        unique=True,
        nullable=False,
        comment="Unique email address.",
    )
    hashed_password: Mapped[str] = mapped_column(
        nullable=False, comment="Hashed password."
    )
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        server_default=sql.false(),
        comment="Indicates if the user is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default=sql.false(),
        comment="Indicates if the user is verified",
    )

    # Relationships
    roles: Mapped[list[Role]] = relationship(
        secondary="account__auth__user_role",
        backref="users",
    )
    token: Mapped[list[Token]] = relationship(
        backref="users",
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        backref="users",
    )

    def __str__(self) -> str:
        """Return a string representation of the User object."""
        return (
            f"<User(username={self.username}, email={self.email}, "
            f"is_active={self.is_active}, is_verified={self.is_verified})>"
        )

    def __repr__(self) -> str:
        """Return a human-readable string representation of the User object."""
        return (
            f"User(username={self.username}, email={self.email}, "
            f"is_active={self.is_active}, is_verified={self.is_verified})"
        )
