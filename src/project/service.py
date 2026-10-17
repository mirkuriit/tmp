import datetime as dt
from uuid import UUID

from src.cache import CacheClient
from src.exceptions import NotFoundException
from src.logger import logger
from src.project.mapper import ProjectMapper
from src.project.model import Project
from src.project.schema import (
    PaginatedProjectResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from src.project.unit_of_work import ProjectUOW


class ProjectService:
    def __init__(self, mapper: ProjectMapper, cache_client: CacheClient, uow: ProjectUOW) -> None:
        self._mapper = mapper
        self._cache_client = cache_client
        self._uow = uow


    async def _get_one(
            self,
            uow: ProjectUOW,
            project_id: UUID,
    ) -> Project:
        project = await uow.repository.get_one_or_none(project_id)
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
        cache_key = self._cache_client.get_one_cache_key(project_id, "project")
        project = await self._cache_client.get_response(cache_key, ProjectResponse)
        if not project:
            async with self._uow as uow:
                project = await self._get_one(uow, project_id)
            project = self._mapper.model_to_schema(project)
            await self._cache_client.set_response(cache_key, project)
        return project

    async def get_many(self, show_after_datetime: dt.datetime | None, show_after_id: UUID | None, limit: int) -> PaginatedProjectResponse:
        cache_key = await self._cache_client.get_many_cache_key("projects", show_after_datetime, show_after_id, limit)
        projects = await self._cache_client.get_response(cache_key, PaginatedProjectResponse)
        if not projects:
            async with self._uow as uow:
                projects = await uow.repository.get_many(show_after_datetime, show_after_id, limit)
                if not projects:
                    raise NotFoundException(
                        detail="Projects not found"
                    )
            projects = self._mapper.models_to_pagination_schema(projects)
            await self._cache_client.set_response(cache_key, projects)
        return projects


    async def create(self, data: ProjectCreate) -> ProjectResponse:
        create_schema = self._mapper.schema_to_model(data)
        async with self._uow as uow:
            project = await uow.repository.create(create_schema)
        await self._cache_client.update_get_many_cache_key_version("projects")
        return self._mapper.model_to_schema(project)


    async def update(self, project_id: UUID, data: ProjectUpdate) -> ProjectResponse:
        async with self._uow as uow:
            project = await self._get_one(uow, project_id)
            await uow.repository.update(project, data)
        project_response = self._mapper.model_to_schema(project)
        await self._cache_client.set_response(
            self._cache_client.get_one_cache_key(project_id, "project"),
            project_response
        )
        await self._cache_client.update_get_many_cache_key_version("projects")
        return project_response
    
    async def delete(
            self,
            project_id: UUID,
            llm_model_id: UUID | None = None
    ) -> ProjectResponse:
        async with self._uow as uow:
            project = await self._get_one(uow, project_id)
            deleted_project = await uow.repository.delete(project, llm_model_id)
        await self._cache_client.delete(self._cache_client.get_one_cache_key(project_id, "project"))
        await self._cache_client.update_get_many_cache_key_version("projects")
        return self._mapper.model_to_schema(deleted_project)
