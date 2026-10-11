import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.schema import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from src.organization.service import OrganizationService
from tests.utils import compare_object_fields


@pytest.fixture(scope="session")
def service(db_session: AsyncSession) -> OrganizationService:
    return OrganizationService(
        OrganizationRepository(db_session),
        OrganizationMapper(),
    )


@pytest.fixture(scope="session")
def repository(db_session: AsyncSession) -> OrganizationRepository:
    return OrganizationRepository(
        db_session
    )


@pytest.fixture(scope="session")
def create_organization_instance() -> OrganizationCreate:
    return OrganizationCreate(
        name="Fish organ",
        description="Organization about fish",
        logo_url="https://example.com/"
    )

@pytest.fixture(scope="session")
def update_organization_instance(created_organization_response: OrganizationResponse) -> OrganizationUpdate:
    return OrganizationUpdate(
        id=created_organization_response.id,
        name="Updated fish inc.",
        description="Updated organization about fish",
        logo_url="https://example.com/updated.png",
    )


@pytest.fixture(scope="session")
async def created_organization_response(
        service: OrganizationService,
        create_organization_instance: OrganizationCreate
) -> OrganizationResponse:
    return await service.create(create_organization_instance)


async def test_create_organization(
        create_organization_instance: OrganizationCreate,
        created_organization_response: OrganizationResponse,
        repository: OrganizationRepository
) -> None:
    organization = await repository.get_one_or_none(created_organization_response.id)
    compare_object_fields(organization, create_organization_instance)


async def test_create_many_organizations(
        service: OrganizationService,
        repository: OrganizationRepository,
) -> None:
    organizations = [
        OrganizationCreate(name="Shark inc.", description="about sharks"),
        OrganizationCreate(name="Whale inc.", description="about whales"),
    ]
    created = await service.create_many(organizations)
    for organization_response, organization_data in zip(created, organizations):
        organization = await repository.get_one_or_none(organization_response.id)
        compare_object_fields(organization, organization_data)


async def test_get_organization(
        create_organization_instance: OrganizationCreate,
        created_organization_response: OrganizationResponse,
        service: OrganizationService,
) -> None:
    organization = await service.get_one(created_organization_response.id)
    compare_object_fields(organization, create_organization_instance)


async def test_get_many_organizations(
        created_organization_response: OrganizationResponse,
        service: OrganizationService,
) -> None:
    organizations = await service.get_many()
    assert created_organization_response.id in {
        organization.id for organization in organizations
    }


async def test_update_organization(
        created_organization_response: OrganizationResponse,
        update_organization_instance: OrganizationUpdate,
        repository: OrganizationRepository,
        service: OrganizationService,
) -> None:
    organization = await repository.get_one_or_none(created_organization_response.id)
    await service.update_many([organization], [update_organization_instance])
    organization = await repository.get_one_or_none(created_organization_response.id)
    compare_object_fields(organization, update_organization_instance)


async def test_delete_organization(
        created_organization_response: OrganizationResponse,
        repository: OrganizationRepository,
        service: OrganizationService,
) -> None:
    await service.delete_many([created_organization_response.id])
    organization = await repository.get_one_or_none(created_organization_response.id)
    assert organization is None
