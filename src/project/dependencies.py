from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient, get_cache_client
from src.db import get_read_session, get_session
from src.project.mapper import ProjectMapper
from src.project.repository import ProjectRepository
from src.project.service import ProjectService


def project_service_dependency(session_dependency: Callable[..., Any]) -> Callable[[AsyncSession], ProjectService]:
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
        cache_client: Annotated[CacheClient, Depends(get_cache_client)],
    ) -> ProjectService:
        repository = ProjectRepository(session)
        mapper = ProjectMapper()

        return ProjectService(repository, mapper, cache_client)

    return dependency


get_read_project_service = project_service_dependency(get_read_session)
get_project_service = project_service_dependency(get_session)