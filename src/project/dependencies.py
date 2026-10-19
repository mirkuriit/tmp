from typing import Annotated

from fastapi import Depends

from src.cache import CacheClient, cache_client_dependency
from src.db import SessionDependency, UnitOfWork, uow_dependency
from src.project.mapper import ProjectMapper
from src.project.repository import ProjectRepository
from src.project.service import ProjectService


def project_repository_dependency(db_session: SessionDependency) -> ProjectRepository:
    return ProjectRepository(db_session)


def project_mapper_dependency() -> ProjectMapper:
    return ProjectMapper()


def project_service_dependency(
        cache_client: Annotated[CacheClient, Depends(cache_client_dependency)],
        mapper: Annotated[ProjectMapper, Depends(project_mapper_dependency)],
        repository: Annotated[ProjectRepository, Depends(project_repository_dependency)],
        uow: Annotated[UnitOfWork, Depends(uow_dependency)]
) -> ProjectService:
    return ProjectService(
        mapper=mapper,
        cache_client=cache_client,
        uow=uow,
        repository=repository
    )