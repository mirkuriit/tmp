from typing import Annotated

from fastapi import Depends

from src.db import SessionDependency
from src.organization.mapper import OrganizationMapper
from src.organization.repository import OrganizationRepository
from src.organization.service import OrganizationService


def organization_repository_dependency(db_session: SessionDependency) -> OrganizationRepository:
    return OrganizationRepository(db_session)


def organization_mapper_dependency() -> OrganizationMapper:
    return OrganizationMapper()


def organization_service_dependency(
        mapper: Annotated[OrganizationMapper, Depends(organization_mapper_dependency)],
        repository: Annotated[OrganizationRepository, Depends(organization_repository_dependency)]
) -> OrganizationService:
    return OrganizationService(repository, mapper)