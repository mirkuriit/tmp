from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from src.cache import CacheClient, get_cache_client
from src.project.factories import ProjectRepositoryFactory
from src.project.mapper import ProjectMapper
from src.project.service import ProjectService
from src.project.unit_of_work import ProjectUOW


def project_service_dependency(request: Request, cache_client: Annotated[CacheClient, Depends(get_cache_client)]) -> ProjectService:
    mapper = ProjectMapper()
    repository_factory = ProjectRepositoryFactory()
    uow = ProjectUOW(request.app.state.SessionFactory, repository_factory)
    return ProjectService(mapper, cache_client, uow)

get_project_service = project_service_dependency