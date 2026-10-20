import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient
from src.db import UnitOfWork
from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.schema import OrganizationCreate
from src.organization.service import OrganizationService
from src.schemas import PaginationPage
from src.user.mapper import UserMapper
from src.user.repository import UserRepository
from src.user.schema import (
    PaginatedUserResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from src.user.service import UserService
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService
from tests.utils import compare_object_fields


@pytest.fixture(scope="session")
def repository(repository_db_session: AsyncSession) -> UserRepository:
    return UserRepository(
        repository_db_session
    )


@pytest.fixture(scope="session")
def service(
        db_session: AsyncSession,
        cache_client: CacheClient,
) -> UserService:
    return UserService(
        repository=UserRepository(db_session),
        mapper=UserMapper(),
        organization_service=OrganizationService(
            OrganizationRepository(db_session),
            OrganizationMapper()
        ),
        user_organization_service=UserOrganizationService(
            UserOrganizationRepository(db_session),
            UserOrganizationMapper()
        ),
        cache_client=cache_client,
        uow=UnitOfWork(db_session)
    )


@pytest.fixture(scope="session")
def create_user_instance() -> UserCreate:
    return UserCreate(
        username="fish_user",
        bio="Дезигнер фром санкт петербург",
        logo_url="https://example.com/",
        has_premium=True,
        organizations=[
            OrganizationCreate(name="Fishes", description="Best fishes in ...")
        ]
    )


@pytest.fixture(scope="session")
def update_user_instance(create_user_instance: UserCreate) -> UserUpdate:
    return UserUpdate(
        username="updated_fish_user",
        bio="Updated дезигнер фром санкт петербург",
        logo_url=create_user_instance.logo_url,
        has_premium=False,
    )


@pytest.fixture(scope="session")
async def created_user_response(
        service: UserService,
        create_user_instance: UserCreate
) -> UserResponse:
    return await service.create(create_user_instance)


async def test_create_user(
        create_user_instance: UserCreate,
        created_user_response: UserResponse,
        repository: UserRepository
) -> None:
    user = await repository.get_one_or_none(created_user_response.id)
    compare_object_fields(
        user, create_user_instance, exclude={"organizations"}
    )
    compare_object_fields(
        user.organizations[0], create_user_instance.organizations[0]
    )


async def test_get_user(
        create_user_instance: UserCreate,
        created_user_response: UserResponse,
        service: UserService,
        cache_client: CacheClient,
) -> None:
    cache_key = cache_client.get_one_cache_key(created_user_response.id, "user")
    await cache_client.delete(cache_key)
    assert await cache_client.get_response(cache_key, UserResponse) is None

    user = await service.get_one(created_user_response.id)
    cached_user = await cache_client.get_response(cache_key, UserResponse)
    assert cached_user is not None
    assert cached_user == user
    compare_object_fields(
        user, create_user_instance, exclude={"organizations"}
    )
    compare_object_fields(
        user.organizations[0], create_user_instance.organizations[0]
    )


async def test_get_many_users(
        created_user_response: UserResponse,
        service: UserService,
        cache_client: CacheClient,
        default_pagination_page: PaginationPage
) -> None:
    cache_key = await cache_client.get_many_cache_key("users", default_pagination_page)
    await cache_client.delete(cache_key)
    assert await cache_client.get_response(cache_key, PaginatedUserResponse) is None

    users = await service.get_many(default_pagination_page)
    cached_users = await cache_client.get_response(cache_key, PaginatedUserResponse)
    assert cached_users is not None
    assert cached_users == users
    for user in users.items:
        if user.id == created_user_response.id:
            compare_object_fields(
                user, created_user_response
            )


async def test_update_user(
        update_user_instance: UserUpdate,
        created_user_response: UserResponse,
        repository: UserRepository,
        service: UserService,
        cache_client: CacheClient,
) -> None:
    cache_key = cache_client.get_one_cache_key(created_user_response.id, "user")
    await service.get_one(created_user_response.id)
    assert await cache_client.get_response(cache_key, UserResponse) is not None

    await service.update(created_user_response.id, update_user_instance)
    user = await repository.get_one_or_none(created_user_response.id)
    compare_object_fields(
        user, update_user_instance, exclude={"organizations"}
    )


async def test_delete_user(
        created_user_response: UserResponse,
        repository: UserRepository,
        service: UserService,
) -> None:
    await service.delete(created_user_response.id)
    user = await repository.get_one_or_none(created_user_response.id)
    assert user is None
