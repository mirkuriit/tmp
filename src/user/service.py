import datetime as dt
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import ColumnElement
from starlette.status import HTTP_409_CONFLICT

from src.exceptions import NotFoundException
from src.logger import logger
from src.organization.service import OrganizationService
from src.user.mapper import UserMapper
from src.user.model import User
from src.user.repository import UserRepository
from src.user.schema import PaginatedUserResponse, UserCreate, UserResponse, UserUpdate
from src.user_organizations.service import UserOrganizationService


class UserService:
    def __init__(
            self,
            repository: UserRepository,
            mapper: UserMapper,
            organization_service: OrganizationService,
            user_organization_service: UserOrganizationService,
    ) -> None:
        self._repository = repository
        self._mapper = mapper
        self._organization_service = organization_service
        self._user_organization_service = user_organization_service


    async def _get_one(
            self,
            user_id: UUID,
            *,
            filters: list[ColumnElement[bool]] | None = None
    ) -> User:
        user = await self._repository.get_one_or_none(user_id, filters=filters)
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
                       show_after_id: UUID | None, limit: int) -> PaginatedUserResponse:
        users = await self._repository.get_many(show_after_datetime,
                                                   show_after_id, limit)
        return self._mapper.models_to_pagination_schema(users)

    async def create(self, data: UserCreate) -> UserResponse:
        user = await self._repository.create(
            self._mapper.schema_to_model(data)
        )
        if not user:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Same user already exists"
            )
        if data.organizations:
            organizations = await self._organization_service.create_many(data.organizations)
            await self._user_organization_service.create_many(
                user_id=user.id,
                organizations=organizations,
            )
        await self._repository.refresh(user)
        return self._mapper.model_to_schema(user)


    async def update(self, user_id: UUID,
                     data: UserUpdate) -> UserResponse:
        if data.username:
            await self._repository.get_advisory_lock(data.username)
            checked_user = await self._repository.get_many(limit=1, filters=[User.username == data.username])
            if checked_user:
                raise HTTPException(
                    detail="User with same username exists",
                    status_code=HTTP_409_CONFLICT
                )

        user = await self._get_one(user_id)
        await self._repository.update(user, data)
        if data.organizations:
            await self._organization_service.update_many(
                user.organizations, data.organizations
            )
        return self._mapper.model_to_schema(user)

    async def delete(
            self,
            user_id: UUID,
            organization_id: UUID | None = None,
    ) -> None:
        if user_id and organization_id:
            await self._organization_service.delete(organization_id)
        elif user_id:
            user = await self._get_one(user_id)
            await self._repository.delete(user)