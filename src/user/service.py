import datetime as dt
from uuid import UUID

from src.cache import CacheClient
from src.exceptions import NotFoundException, ResourceExistsException
from src.logger import logger
from src.user.mapper import UserMapper
from src.user.model import User
from src.user.schema import PaginatedUserResponse, UserCreate, UserResponse, UserUpdate
from src.user.unit_of_work import UserUOW


class UserService:
    def __init__(
            self,
            mapper: UserMapper,
            cache_client: CacheClient,
            uow: UserUOW
    ) -> None:
        self._mapper = mapper
        self._cache_client = cache_client
        self._uow = uow

    async def _get_one(
            self,
            uow: UserUOW,
            user_id: UUID,
    ) -> User:
        user = await uow.repository.get_one_or_none(user_id)
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
        cache_key = self._cache_client.get_one_cache_key(user_id, "user")
        user = await self._cache_client.get_response(cache_key, UserResponse)
        if not user:
            async with self._uow as uow:
                user = await self._get_one(uow, user_id)
            user = self._mapper.model_to_schema(user)
            await self._cache_client.set_response(cache_key, user)
        return user

    async def get_many(self, show_after_datetime: dt.datetime | None,
                       show_after_id: UUID | None,
                       limit: int) -> PaginatedUserResponse:
        cache_key = await self._cache_client.get_many_cache_key(
            "users",
            show_after_datetime,
            show_after_id,
            limit
        )
        users = await self._cache_client.get_response(
            cache_key,
            PaginatedUserResponse
        )
        if not users:
            async with self._uow as uow:
                users = await uow.repository.get_many(
                    limit=limit,
                    show_after_datetime=show_after_datetime,
                    show_after_id=show_after_id,
                )
            if not users:
                raise NotFoundException(
                    detail="Users not found",
                )
            users = self._mapper.models_to_pagination_schema(users)
            await self._cache_client.set_response(cache_key, users)
        return users

    async def create(self, data: UserCreate) -> UserResponse:
        create_schema = self._mapper.schema_to_model(data)
        async with self._uow as uow:
            user = await uow.repository.create(
                create_schema
            )
            if not user:
                raise ResourceExistsException(
                    detail="Same unique field already exists"
                )
            if data.organizations:
                organizations = await uow.organization_service.create_many(
                    data.organizations)
                await uow.user_organization_service.create_many(
                    user_id=user.id,
                    organizations=organizations,
                )
            await uow.repository.refresh(user)
        await self._cache_client.update_get_many_cache_key_version("users")
        return self._mapper.model_to_schema(user)

    async def update(self, user_id: UUID,
                     data: UserUpdate) -> UserResponse:
        async with self._uow as uow:
            if data.username:
                await uow.repository.get_advisory_lock(
                    f"{User.__tablename__}:{data.username}")
                checked_user = await uow.repository.get_many(limit=1, filters=[
                    User.username == data.username, User.id != user_id])
                if checked_user:
                    raise ResourceExistsException(
                        detail="User with same username exists",
                    )

            user = await self._get_one(uow, user_id)
            await uow.repository.update(user, data)
            if data.organizations:
                await uow.organization_service.update_many(
                    user.organizations, data.organizations
                )
        user_response = self._mapper.model_to_schema(user)
        cache_key = self._cache_client.get_one_cache_key(user_id, "user")
        await self._cache_client.set_response(cache_key, user_response)
        await self._cache_client.update_get_many_cache_key_version("users")
        return user_response

    async def delete(
            self,
            user_id: UUID,
            organization_id: UUID | None = None,
    ) -> None:
        async with self._uow as uow:
            if user_id and organization_id:
                await uow.organization_service.delete_many([organization_id])
                await uow.user_organization_service.delete_many(user_id,
                                                                  [organization_id])
            elif user_id:
                user = await self._get_one(uow, user_id)
                await uow.repository.delete(user)
                await uow.user_organization_service.delete_many(
                    user_id,
                    [organization.id for organization in user.organizations]
                )
        await self._cache_client.delete(
            self._cache_client.get_one_cache_key(user_id, "user")
        )
        await self._cache_client.update_get_many_cache_key_version("users")