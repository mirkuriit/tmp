from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.db import get_session
from src.project.project_repository import ProjectRepository
from src.project.project_service import ProjectService


def depends_project_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> ProjectRepository:
    return ProjectRepository(session)


def depends_project_service(repository: Annotated[ProjectRepository, Depends(depends_project_repository)]):
    return ProjectService(repository)