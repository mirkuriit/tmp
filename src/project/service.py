from uuid import UUID

from src.project.exceptions import ProjectNotFoundException
from src.project.mapper import ProjectMapper
from src.project.model import Project
from src.project.repository import ProjectRepository
from src.project.schema import ProjectCreate, ProjectUpdate, ProjectResponse


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self._repository = repository


    async def _get_one(self, project_id: UUID) -> Project:
        project = await self._repository.get_one_or_none(project_id)
        if project is None:
            raise ProjectNotFoundException(detail="Project not found")
        return project


    async def get_one(self, project_id: UUID) -> ProjectResponse:
        project = await self._get_one(project_id)
        return ProjectMapper.model_to_schema(project)

    
    async def create(self, data: ProjectCreate) -> ProjectResponse:
        project = await self._repository.create(ProjectMapper.schema_to_model(data))
        return ProjectMapper.model_to_schema(project)


    async def update(self, project_id: UUID, data: ProjectUpdate) -> ProjectResponse:
        project = await self._get_one(project_id)
        await self._repository.update(project, data)
        return ProjectMapper.model_to_schema(project)
    
    
    async def delete(self, project_id: UUID) -> ProjectResponse:
        project = await self._get_one(project_id)
        deleted_project = await self._repository.delete(project)
        return ProjectMapper.model_to_schema(deleted_project)

