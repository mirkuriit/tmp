from typing import Annotated

from fastapi import Depends

from src.cache import CacheClient, cache_client_dependency
from src.db import SessionDependency, UnitOfWork, uow_dependency
from src.organization.dependencies import organization_service_dependency
from src.organization.service import OrganizationService
from src.user.mapper import UserMapper
from src.user.repository import UserRepository
from src.user.service import UserService
from src.user_organizations.dependencies import user_organization_service_dependency
from src.user_organizations.service import UserOrganizationService


def user_repository_dependency(session: SessionDependency) -> UserRepository:
    return UserRepository(session)

def user_mapper_dependency() -> UserMapper:
    return UserMapper()


def user_service_dependency(
        cache_client: Annotated[CacheClient, Depends(cache_client_dependency)],
        repository: Annotated[UserRepository, Depends(user_repository_dependency)],
        mapper: Annotated[UserMapper, Depends(user_mapper_dependency)],
        uow: Annotated[UnitOfWork, Depends(uow_dependency)],
        organization_service: Annotated[OrganizationService, Depends(organization_service_dependency)],
        user_organization_service: Annotated[UserOrganizationService, Depends(user_organization_service_dependency)]
) -> UserService:
    return UserService(
        mapper=mapper,
        cache_client=cache_client,
        uow=uow,
        repository=repository,
        organization_service=organization_service,
        user_organization_service=user_organization_service,
    )