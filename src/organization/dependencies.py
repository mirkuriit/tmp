from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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