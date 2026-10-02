import datetime as dt
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_409_CONFLICT

from src.exceptions import NotFoundException, ResourceIsLockedException
from src.logger import logger
from src.organization.repository import OrganizationRepository
from src.organization.service import OrganizationService
from src.user.mapper import UserMapper
from src.user.model import User
from src.user_organizations.model import UserOrganization
from src.user.repository import UserRepository
from src.user.schema import PaginatedUserResponse, UserCreate, UserResponse, UserUpdate
from src.user_organizations.repository import UserOrganizationRepository
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
            need_advisory_lock: bool = False,
            lock_key: str | None = None
    ) -> User:
        user = await self._repository.get_one_or_none(user_id, need_advisory_lock=need_advisory_lock, lock_key=lock_key)
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
            user_organizations = await self._user_organization_service.create_many(
                user_id=user.id,
                organizations=organizations,
            )
        await self._repository.refresh(user)
        return self._mapper.model_to_schema(user)

    async def update(self, user_id: UUID,
                     data: UserUpdate) -> UserResponse:
        try:
            user = await self._get_one(user_id, need_advisory_lock=True, lock_key=data.username)
            await self._repository.update(user, data)
            return self._mapper.model_to_schema(user)
        except ResourceIsLockedException as ex:
            logger.exception(f"Resource: user with id {user_id} is locked")
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail="Internal user update error. Retry later."
            ) from ex
        except IntegrityError as ex:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=f"{ex}",
            ) from ex

