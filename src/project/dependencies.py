from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_read_session, get_session
from src.project.repository import ProjectRepository
from src.project.service import ProjectService


def project_service_dependency(session_dependency):
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> ProjectService:
        repository = ProjectRepository(session)
        return ProjectService(repository)

    return dependency


get_read_project_service = project_service_dependency(get_read_session)
get_project_service = project_service_dependency(get_session)