from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.cache import CacheClient, get_cache_client
from src.db import get_read_session, get_session
from src.project.mapper import ProjectMapper
from src.project.repository import ProjectRepository
from src.project.service import ProjectService
from src.project.unit_of_work import ProjectUOW
from src.project.factories import ProjectRepositoryFactory


def project_service_dependency(request: Request, cache_client: Annotated[CacheClient, Depends(get_cache_client)]) -> ProjectService:
    mapper = ProjectMapper()
    repository_factory = ProjectRepositoryFactory()
    uow = ProjectUOW(request.app.state.SessionFactory, repository_factory)
    return ProjectService(mapper, cache_client, uow)

get_project_service = project_service_dependency