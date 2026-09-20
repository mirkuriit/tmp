import datetime as dt
from uuid import UUID

from src.exceptions import NotFoundException
from src.logger import logger
from src.project.mapper import ProjectMapper
from src.project.model import Project
from src.project.repository import ProjectRepository
from src.project.schema import (
    PaginatedProjectResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectService:
    def __init__(self, repository: ProjectRepository, mapper: ProjectMapper) -> None:
        self._mapper = mapper
        self._repository = repository


    async def _get_one(
            self,
            project_id: UUID,
    ) -> Project:
        project = await self._repository.get_one_or_none(project_id)
        if project is None:
            detail = f"Project with id: {project_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return project


    async def get_one(self, project_id: UUID) -> ProjectResponse:
        project = await self._get_one(project_id)
        return self._mapper.model_to_schema(project)

    async def get_many(self, show_after_datetime: dt.datetime | None, show_after_id: UUID | None, limit: int) -> PaginatedProjectResponse:
        projects = await self._repository.get_many(show_after_datetime, show_after_id, limit)
        return self._mapper.models_to_pagination_schema(projects)


    async def create(self, data: ProjectCreate) -> ProjectResponse:
        project = await self._repository.create(self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(project)


    async def update(self, project_id: UUID, data: ProjectUpdate) -> ProjectResponse:
        project = await self._get_one(project_id)
        await self._repository.update(project, data)
        return self._mapper.model_to_schema(project)
    
    
    async def delete(
            self,
            project_id: UUID,
            llm_model_id: UUID | None = None
    ) -> ProjectResponse:
        project = await self._get_one(project_id)
        deleted_project = await self._repository.delete(project, llm_model_id)
        return self._mapper.model_to_schema(deleted_project)
