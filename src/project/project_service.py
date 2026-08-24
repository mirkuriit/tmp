from uuid import UUID

from project.project_repository import ProjectRepository
from src.project.project_model import Project
from src.project.project_schema import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository
    
    
    async def create(self, data: ProjectCreate) -> Project:
        return await self.repository.create(data)


    async def get_one(self, project_id: UUID) -> Project:
        return await self.repository.get_one(project_id)


    async def update(self, project_id: UUID, data: ProjectUpdate) -> Project:
        return await self.repository.update(project_id, data)
    
    
    async def delete(self, project_id: UUID) -> None:
        await self.repository.delete(project_id)
    