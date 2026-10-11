import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.schema import OrganizationCreate, OrganizationResponse
from src.organization.service import OrganizationService
from src.user.model import User
from src.user.repository import UserRepository
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.schema import (
    UserOrganizationResponse,
)
from src.user_organizations.service import UserOrganizationService
from tests.utils import compare_object_fields


@pytest.fixture(scope="session")
def service(db_session: AsyncSession) -> UserOrganizationService:
    return UserOrganizationService(
        UserOrganizationRepository(db_session),
        UserOrganizationMapper()
    )


@pytest.fixture(scope="session")
def repository(db_session: AsyncSession) -> UserOrganizationRepository:
    return UserOrganizationRepository(
        db_session
    )


@pytest.fixture(scope="session")
def organization_repository(db_session: AsyncSession) -> OrganizationRepository:
    return OrganizationRepository(
        db_session
    )


@pytest.fixture(scope="session")
def organization_service(db_session: AsyncSession, organization_repository: OrganizationRepository) -> OrganizationService:
    return OrganizationService(
        organization_repository,
        OrganizationMapper(),
    )


@pytest.fixture(scope="session")
def user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(
        db_session
    )



@pytest.fixture(scope="session")
async def user(db_session: AsyncSession, user_repository: UserRepository) -> User:
    return await user_repository.create(
        User(username="user_org_fish", has_premium=False)
    )


@pytest.fixture(scope="session")
async def created_organizations_response(db_session: AsyncSession, organization_service: OrganizationService) -> list[OrganizationResponse]:
    return await organization_service.create_many(
        [
            OrganizationCreate(name="First fish org"),
            OrganizationCreate(name="Second fish org"),
         ]
    )


@pytest.fixture(scope="session")
async def created_user_organizations_response(
        service: UserOrganizationService,
        user: User,
        created_organizations_response: list[OrganizationResponse],
) -> list[UserOrganizationResponse]:
    return await service.create_many(
        user.id,
        created_organizations_response,
    )


async def test_create_many_user_organization(
        user: User,
        created_user_organizations_response: list[UserOrganizationResponse],
        repository: UserOrganizationRepository,
) -> None:
    user_organizations = await repository.get_by_user_id(
        user.id
    )
    for user_organization, created_user_organization_response in zip(user_organizations, created_user_organizations_response):
        compare_object_fields(user_organization, created_user_organization_response)



async def test_delete_many_user_organizations(
        user: User,
        created_organizations_response: OrganizationResponse,
        service: UserOrganizationService,
        repository: UserOrganizationRepository,
) -> None:
    organization_ids = [organization.id for organization in created_organizations_response]
    await service.delete_many(user.id, organization_ids)
    for organization_id in organization_ids:
        assert await repository.get_one_or_none(user.id, organization_id) is None
