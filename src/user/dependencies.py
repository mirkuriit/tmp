from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_read_session, get_session
from src.user.mapper import UserMapper
from src.user.repository import UserRepository
from src.user.service import UserService


def user_service_dependency(session_dependency):
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> UserService:
        repository = UserRepository(session)
        mapper = UserMapper()
        return UserService(repository, mapper)

    return dependency


get_read_user_service = user_service_dependency(get_read_session)
get_user_service = user_service_dependency(get_session)