from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.llm_models.model import LLMModel
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
    ):
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
        project = ProjectMapper.update_model_from_schema(project, updated_schema)
        await self._session.flush()
        return project


    async def delete(self, project: Project) -> Project:
        project.is_deleted = True
        await self._session.flush()
        return project


    async def delete_llm_model(self, llm_model: LLMModel) -> LLMModel:
        llm_model.is_deleted = True
        await self._session.flush()
        return llm_model


    async def get_llm_models_by_project_id(
            self,
            project_id: UUID,
            *,
            page: int | None = None,
            size: int | None = None,
            is_deleted: bool = False,
    )-> list[LLMModel]:
        filters = [
            LLMModel.project_id == project_id,
            LLMModel.is_deleted == is_deleted
        ]
        select_statement = select(LLMModel).where(*filters).order_by(LLMModel.id)
        if page and size:
            select_statement = select_statement.limit(size).offset((page - 1) * size)
        return list(await self._session.scalars(select_statement))
    
