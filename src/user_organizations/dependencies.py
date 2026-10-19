from typing import Annotated

from fastapi import Depends

from src.db import SessionDependency
from src.user_organizations.mapper import UserOrganizationMapper
from src.user_organizations.repository import UserOrganizationRepository
from src.user_organizations.service import UserOrganizationService


def user_organization_repository_dependency(db_session: SessionDependency) -> UserOrganizationRepository:
    return UserOrganizationRepository(db_session)


def user_organization_mapper_dependency() -> UserOrganizationMapper:
    return UserOrganizationMapper()


def user_organization_service_dependency(
        repository: Annotated[UserOrganizationRepository, Depends(user_organization_repository_dependency)],
        mapper: Annotated[UserOrganizationMapper, Depends(user_organization_mapper_dependency)],
) -> UserOrganizationService:
    return UserOrganizationService(repository, mapper)
