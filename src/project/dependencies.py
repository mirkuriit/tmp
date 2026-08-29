from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.project.repository import ProjectRepository
from src.project.service import ProjectService


def depends_project_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ProjectRepository:
    return ProjectRepository(session)


def depends_project_service(repository: Annotated[ProjectRepository, Depends(depends_project_repository)]):
    return ProjectService(repository)