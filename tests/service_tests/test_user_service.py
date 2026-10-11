import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient
from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.schema import OrganizationCreate
from src.organization.service import OrganizationService
from src.user.mapper import UserMapper
from src.user.repository import UserRepository
from src.user.schema import UserCreate, UserResponse, UserUpdate
from src.user.service import UserService
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService
from tests.utils import compare_object_fields


@pytest.fixture(scope="session")
def service(db_session: AsyncSession, cache_client: CacheClient) -> UserService:
    return UserService(
        UserRepository(db_session),
        UserMapper(),
        OrganizationService(
            OrganizationRepository(db_session),
            OrganizationMapper()
        ),
        UserOrganizationService(
            UserOrganizationRepository(db_session),
            UserOrganizationMapper()
        ),
        cache_client
    )


@pytest.fixture(scope="session")
def repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(
        db_session
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
) -> None:
    user = await service.get_one(created_user_response.id)
    compare_object_fields(
        user, create_user_instance, exclude={"organizations"}
    )
    compare_object_fields(
        user.organizations[0], create_user_instance.organizations[0]
    )


async def test_get_many_users(
        created_user_response: UserResponse,
        service: UserService,
) -> None:
    users = await service.get_many(None, None, 10)
    for user in users.items:
        if user.id == created_user_response.id:
            compare_object_fields(
                users.items[0], created_user_response
            )


async def test_update_user(
        update_user_instance: UserUpdate,
        created_user_response: UserResponse,
        repository: UserRepository,
        service: UserService,
) -> None:
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
