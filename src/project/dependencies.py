from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import cache_client
from src.db import get_read_session, get_session
from src.project.mapper import ProjectMapper
from src.project.repository import ProjectRepository
from src.project.service import ProjectService


def project_service_dependency(session_dependency: Callable[..., Any]) -> Callable[[AsyncSession], ProjectService]:
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> ProjectService:
        repository = ProjectRepository(session)
        mapper = ProjectMapper()

        project_cache_client = cache_client
        return ProjectService(repository, mapper, project_cache_client)

    return dependency


get_read_project_service = project_service_dependency(get_read_session)
get_project_service = project_service_dependency(get_session)