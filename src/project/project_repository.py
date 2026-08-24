from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import update, select

from src.project.project_model import Project
from src.project.project_schema import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def __init__(self, db_session: AsyncSession):
        self._session = db_session


    async def create(self, data: ProjectCreate) -> Project:
        project = Project(**data.model_dump())
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return project


    async def update(self, project_id: UUID, data: ProjectUpdate) -> Project:
        stmt = update(Project).where(Project.id == project_id).values(**data.model_dump()).returning(Project)
        res = await self._session.execute(stmt)
        await self._session.commit()
        return res.scalar_one()
    

    async def delete(self, project_id: UUID) -> None:
        project = await self._session.scalar(select(Project).where(Project.id == project_id))
        project.is_deleted = True
        await self._session.commit()


    async def get_one(self,  project_id: UUID) -> Optional[Project] | None:
        project = await self._session.scalar(select(Project).where(Project.id == project_id, Project.is_deleted == False))
        return project
    
