import datetime as dt
from uuid import UUID

from sqlalchemy import Sequence, and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.project.mapper import ProjectMapper
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

    async def get_many(self, show_after_datetime: dt.datetime | None, show_after_id: UUID | None,  limit: int) -> Sequence[Project]:
        statement = select(
            Project
        ).order_by(
            Project.created_at,
            Project.id
        ).limit(
            limit
        ).where(
            Project.is_deleted == False
        )
        if show_after_datetime and show_after_id:
            statement = statement.where(
                or_(
                    Project.created_at > show_after_datetime,
                    and_(
                        Project.created_at == show_after_datetime,
                        Project.id > show_after_id
                    )
                )
            )

        return (await self._session.scalars(statement)).all()

    async def create(self, project: Project) -> Project:
        self._session.add(project)
        await self._session.flush()
        return project


    async def update(self, project: Project, updated_schema: ProjectUpdate) -> Project:
        project = ProjectMapper.update_model_from_schema(project, updated_schema)
        await self._session.flush()
        return project


    async def delete(self, project: Project, llm_model_id: UUID | None = None) -> Project:
        if project and llm_model_id is None:
            project.is_deleted = True
        for model in project.llm_models:
            if model.id == llm_model_id or llm_model_id is None:
                model.is_deleted = True
        await self._session.flush()
        return project
    
