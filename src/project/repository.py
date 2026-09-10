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
        project_filters = [
            Project.id == project_id,
            Project.is_deleted == is_deleted
        ]
        return await self._session.scalar(select(Project).where(*project_filters))


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
        for llm_model in project.llm_models:
            llm_model.is_deleted = True

        await self._session.flush()
        return project


    async def get_llm_models_by_project_id(
            self,
            project_id: UUID,
            *,
            llm_model_page: int | None = None,
            llm_model_size: int | None = None,
            is_deleted: bool = False,
    )-> list[LLMModel]:
        llm_model_filters = [
            LLMModel.project_id == project_id,
            LLMModel.is_deleted == is_deleted
        ]
        llm_model_select_statement = select(LLMModel).where(*llm_model_filters).order_by(LLMModel.id)
        if llm_model_page and llm_model_size:
            llm_model_select_statement = llm_model_select_statement.limit(llm_model_size).offset((llm_model_page-1)*llm_model_size)
        return list(await self._session.scalars(llm_model_select_statement))
    
