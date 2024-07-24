"""Module containing model definitions for User."""

from sqlalchemy.orm import Mapped, mapped_column

from config.database.annotations import str255
from config.database.orm import Base
from toolkit.database.mixins import CommonMixin


class User(CommonMixin, Base):
    """Represents a user in the authentication system."""

    __tablename__ = "account__auth__user"

    # Columns
    username: Mapped[str255] = mapped_column(
        unique=False,
        nullable=False,
        comment="Unique username.",
    )
    email: Mapped[str255] = mapped_column(
        unique=False,
        nullable=False,
        comment="Unique email address.",
    )
    hashed_password: Mapped[str] = mapped_column(
        nullable=False, comment="Hashed password."
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="Indicates if the user is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        comment="Indicates if the user is verified",
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
