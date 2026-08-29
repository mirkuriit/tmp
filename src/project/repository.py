from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.project.model import Project
from src.project.schema import ProjectUpdate


class ProjectRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session


    async def get_one_or_none(
            self,
            project_id: UUID,
            *,
            is_deleted: bool = False,
    ) -> Project | None:
        filters = [
            Project.id == project_id,
            Project.is_deleted == is_deleted
        ]

        return await self._session.scalar(select(Project).where(*filters))


    async def create(self, project: Project) -> Project:
        self._session.add(project)
        await self._session.flush()
        return project


    async def update(self, project: Project, updated_schema: ProjectUpdate):
        for field, value in updated_schema.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        await self._session.flush()
        return project


    async def delete(self, project: Project) -> Project:
        project.is_deleted = True
        await self._session.flush()
        return project
    
