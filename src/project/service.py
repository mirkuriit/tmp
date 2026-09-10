from uuid import UUID

from src.exceptions import NotFoundException
from src.logger import logger
from src.project.mapper import ProjectMapper
from src.project.model import Project
from src.project.repository import ProjectRepository
from src.project.schema import ProjectCreate, ProjectResponse, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository, mapper: ProjectMapper) -> None:
        self._mapper = mapper
        self._repository = repository


    async def _get_one(
            self,
            project_id: UUID,
    ) -> Project:
        project = await self._repository.get_one_or_none(project_id,)
        if project is None:
            detail = f"Project with id: {project_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return project


    async def get_one_with_pagination(
            self,
            project_id: UUID,
            llm_model_page: int | None = None,
            llm_model_size: int | None = None
    ) -> ProjectResponse:
        project = await self._repository.get_one_or_none(
            project_id
        )
        if project is None:
            detail = f"Project with id: {project_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        llm_models = await self._repository.get_llm_models_by_project_id(
            project_id,
            page=llm_model_page,
            size=llm_model_size,
        )
        project.llm_models = llm_models
        return self._mapper.model_to_schema(project)

    
    async def create(self, data: ProjectCreate) -> ProjectResponse:
        project = await self._repository.create(self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(project)


    async def update(self, project_id: UUID, data: ProjectUpdate) -> ProjectResponse:
        project = await self._get_one(project_id)
        await self._repository.update(project, data)
        return self._mapper.model_to_schema(project)
    
    
    async def delete(self, project_id: UUID) -> ProjectResponse:
        project = await self._get_one(project_id)
        deleted_project = await self._repository.delete(project)
        return self._mapper.model_to_schema(deleted_project)


    async def delete_llm_model(self, project_id: UUID, llm_model_id: UUID) -> ProjectResponse:
        project = await self._get_one(project_id)
        deleted_project = await self._repository.delete(project)
        return self._mapper.model_to_schema(deleted_project)
