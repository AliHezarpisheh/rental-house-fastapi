"""Module containing dependency services for the auth API."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from app.account.auth.repository.services import UserService
from toolkit.api.database import get_async_db_session


async def get_user_service(
    db_session: Annotated[
        async_scoped_session[AsyncSession], Depends(get_async_db_session)
    ],
) -> UserService:
    """Get UserService dependency, injecting db session."""
    return UserService(db_session=db_session)
