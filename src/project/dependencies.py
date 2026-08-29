from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.project.repository import ProjectRepository
from src.project.service import ProjectService


def depends_project_repository(read_only: bool = False) -> Callable:
    def get_project_repository(session: Annotated[AsyncSession, Depends(get_session(read_only=False))]) -> ProjectRepository:
        return ProjectRepository(session)
    def get_project_repository_read_only(session: Annotated[AsyncSession, Depends(get_session(read_only=True))]) -> ProjectRepository:
        return ProjectRepository(session)
    if read_only:
        return get_project_repository_read_only
    return get_project_repository


def depends_project_service(read_only: bool = False) -> Callable:
    def get_project_service(repository: Annotated[ProjectRepository, Depends(depends_project_repository(read_only=False))]):
        return ProjectService(repository)
    def get_project_service_read_only(repository: Annotated[ProjectRepository, Depends(depends_project_repository(read_only=True))]):
        return ProjectService(repository)
    if read_only:
        return  get_project_service_read_only
    return get_project_service