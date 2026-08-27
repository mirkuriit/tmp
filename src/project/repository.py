from uuid import UUID

from sqlalchemy import select, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from src.project.exceptions import ProjectNotFoundException
from src.project.model import Project
from src.project.schema import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session


    async def _get_one(
            self,
            project_id: UUID,
            is_deleted: bool = True,
    ) -> Project | None:
        filters = [
            Project.id == project_id,
            Project.is_deleted == is_deleted
        ]

        return await self._session.scalar(select(Project).where(*filters))


    async def create(self, data: ProjectCreate) -> Project:
        project = Project(**data.model_dump())
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return project


    async def update(self, project_id: UUID, data: ProjectUpdate) -> Project | None:
        project = await self.get_one(project_id)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)

        await self._session.flush()
        await self._session.commit()
        return project
    

    async def delete(self, project_id: UUID) -> None:
        project = await self.get_one(project_id)
        ### TODO сделать чтобы исключение на отсуствие объекта кидалось на уровне сервиса
        project.is_deleted = True
        await self._session.commit()


    async def get_one(self,  project_id: UUID) -> Project | None:
        project = await self.get_one(project_id)
        return project
    
