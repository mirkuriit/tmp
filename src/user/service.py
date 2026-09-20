import datetime as dt
from uuid import UUID

from src.exceptions import NotFoundException
from src.logger import logger
from src.user.mapper import UserMapper
from src.user.model import User
from src.user.repository import UserRepository
from src.user.schema import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository,
                 mapper: UserMapper) -> None:
        self._mapper = mapper
        self._repository = repository

    async def _get_one(
            self,
            user_id: UUID,
    ) -> User:
        user = await self._repository.get_one_or_none(user_id)
        if user is None:
            detail = f"User with id: {user_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return user

    async def get_one(self, user_id: UUID) -> UserResponse:
        user = await self._get_one(user_id)
        return self._mapper.model_to_schema(user)

    async def get_many(self, show_after_datetime: dt.datetime | None,
                       show_after_id: UUID | None, limit: int):
        users = await self._repository.get_many(show_after_datetime,
                                                   show_after_id, limit)
        return self._mapper.models_to_pagination_schema(users)

    async def create(self, data: UserCreate) -> UserResponse:
        user = await self._repository.create(
            self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(user)

    async def update(self, user_id: UUID,
                     data: UserUpdate) -> UserResponse:
        user = await self._get_one(user_id)
        await self._repository.update(user, data)
        return self._mapper.model_to_schema(user)

    async def delete(
            self,
            user_id: UUID,
            organization_id: UUID | None = None
    ) -> UserResponse:
        user = await self._get_one(user_id)
        deleted_user = await self._repository.delete(user, organization_id)
        return self._mapper.model_to_schema(deleted_user)
