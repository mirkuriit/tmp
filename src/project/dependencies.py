from fastapi import Depends

from src.db import get_session
from src.project.project_repository import ProjectRepository
from src.project.project_service import ProjectService

from sqlalchemy.ext.asyncio import AsyncSession

def depends_project_repository(session: AsyncSession = Depends(get_session)) -> ProjectRepository:
    return ProjectRepository(session)


def depends_project_service(repository: ProjectRepository = Depends(depends_project_repository)):
    return ProjectService(repository)