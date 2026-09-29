import datetime as dt
from uuid import UUID

from fastapi import HTTPException
from starlette.status import HTTP_409_CONFLICT

from src.exceptions import NotFoundException, ResourceIsLockedException
from src.logger import logger
from src.user.mapper import UserMapper
from src.user.model import User, UserOrganization
from src.user.repository import UserRepository
from src.user.schema import PaginatedUserResponse, UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, repository: UserRepository,
                 mapper: UserMapper) -> None:
        self._mapper = mapper
        self._repository = repository

    async def connect_organizations_to_user(
            self,
            user_id,
            organization_ids: list[UUID]
    ) -> UserResponse:
        for organization_id in organization_ids:
            await self._repository.connect_organization_to_user(
                UserOrganization(user_id=user_id, organization_id=organization_id)
            )
        user = await self.get_one(user_id)
        return user


    async def _get_one(
            self,
            user_id: UUID,
            *,
            need_advisory_lock: bool = False
    ) -> User:
        user = await self._repository.get_one_or_none(user_id, need_advisory_lock=need_advisory_lock)
        if user is None:
            detail = f"User with id: {user_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return user

    async def get_locked_one(self, user_id: UUID) -> UserResponse:
        user = await self._get_one(user_id)
        return self._mapper.model_to_schema(user)

    async def get_one(self, user_id: UUID) -> UserResponse:
        user = await self._get_one(user_id)
        return self._mapper.model_to_schema(user)

    async def get_many(self, show_after_datetime: dt.datetime | None,
                       show_after_id: UUID | None, limit: int) -> PaginatedUserResponse:
        users = await self._repository.get_many(show_after_datetime,
                                                   show_after_id, limit)
        return self._mapper.models_to_pagination_schema(users)

    async def create(self, data: UserCreate) -> UserResponse:
        user = await self._repository.create(self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(user)

    async def update(self, user_id: UUID,
                     data: UserUpdate) -> UserResponse:
        try:
            user = await self._get_one(user_id, need_advisory_lock=True)
            await self._repository.update(user, data)
            return self._mapper.model_to_schema(user)
        except ResourceIsLockedException:
            logger.exception(f"Resource: user with id {user_id} is locked")
        raise HTTPException(
            status_code=HTTP_409_CONFLICT,
            detail="Internal user update error. Retry later."
        )


    async def delete(
            self,
            user_id: UUID,
    ) -> UserResponse:
        user = await self._get_one(user_id)
        deleted_user = await self._repository.delete(user)
        return self._mapper.model_to_schema(deleted_user)
