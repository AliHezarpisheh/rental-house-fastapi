"""Module containing model definitions for ActivityLogs."""

from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from config.database.annotations import str255, text
from config.database.orm import Base
from toolkit.database.mixins import IdMixin


class ActivityLog(IdMixin, Base):
    """Model class representing user activities information."""

    __tablename__ = "account__auth__activity_log"

    # Columns
    user_id: Mapped[int] = mapped_column(
        ForeignKey("account__auth__user.id"),
        primary_key=True,
        nullable=False,
        comment="Foreign key referencing users table",
    )
    action: Mapped[str255] = mapped_column(
        nullable=False,
        comment="Description of the action performed",
    )
    ip_address: Mapped[str] = mapped_column(
        nullable=False,
        comment="IP address from where the action was performed",
    )
    user_agent: Mapped[text | None] = mapped_column(
        nullable=True,
        comment="User agent string of the client",
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the record was created",
    )

    def __str__(self) -> str:
        """Return a string representation of the ActivityLog object."""
        return f"<ActivityLog(user_id={self.user_id}, action={self.action})>"

    def __repr__(self) -> str:
        """Return a human-readable string representation of the ActivityLog object."""
        return f"ActivityLog(user_id={self.user_id}, action={self.action})"
