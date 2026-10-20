from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient
from src.db import UnitOfWork
from src.llm_models.schema import LLMModelCreate
from src.project.mapper import ProjectMapper
from src.project.repository import ProjectRepository
from src.project.schema import (
    PaginatedProjectResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from src.project.service import ProjectService
from src.schemas import PaginationPage
from tests.utils import compare_object_fields


@pytest.fixture(scope="session")
def repository(repository_db_session: AsyncSession) -> ProjectRepository:
    return ProjectRepository(
        repository_db_session
    )


@pytest.fixture(scope="session")
def service(
        db_session: AsyncSession,
        cache_client: CacheClient,
) -> ProjectService:
    return ProjectService(
        ProjectMapper(),
        cache_client,
        ProjectRepository(db_session),
        UnitOfWork(db_session)
    )


@pytest.fixture(scope="session")
def create_project_instance() -> ProjectCreate:
    return ProjectCreate(
        name="The fish",
        allow_experimental_functions=True,
        description=" about fish",
        logo_url=None,
        llm_models=[
            LLMModelCreate(
                name="Claude fish",
                base_api_url="https://example.com/",
                token_cost=Decimal('0.1')
            )
        ]
    )


@pytest.fixture(scope="session")
def update_project_instance(create_project_instance: ProjectCreate) -> ProjectUpdate:
    return ProjectUpdate(
        name="Updated the fish",
        description="Updated project about fish",
        allow_experimental_functions=False,
        logo_url=create_project_instance.logo_url
    )


@pytest.fixture(scope="session")
async def created_project_response(
        service: ProjectService,
        create_project_instance: ProjectCreate
)-> ProjectResponse:
    return await service.create(create_project_instance)


async def test_create_project(
        create_project_instance: ProjectCreate,
        created_project_response: ProjectResponse,
        repository: ProjectRepository
) -> None:
    project = await repository.get_one_or_none(created_project_response.id)
    compare_object_fields(
        project, create_project_instance, exclude={"llm_models"}
    )


async def test_get_project(
        create_project_instance: ProjectCreate,
        created_project_response: ProjectResponse,
        repository: ProjectRepository,
        service: ProjectService,
        cache_client: CacheClient,
) -> None:
    cache_key = cache_client.get_one_cache_key(created_project_response.id, "project")
    await cache_client.delete(cache_key)
    assert await cache_client.get_response(cache_key, ProjectResponse) is None

    project = await service.get_one(created_project_response.id)
    cached_project = await cache_client.get_response(cache_key, ProjectResponse)
    assert cached_project is not None
    assert cached_project == project
    compare_object_fields(
        project, create_project_instance, exclude={"llm_models"}
    )


async def test_get_many_projects(
        created_project_response: ProjectResponse,
        service: ProjectService,
        cache_client: CacheClient,
        default_pagination_page: PaginationPage
) -> None:
    cache_key = await cache_client.get_many_cache_key("projects", default_pagination_page)
    await cache_client.delete(cache_key)
    assert await cache_client.get_response(cache_key, PaginatedProjectResponse) is None

    projects = await service.get_many(default_pagination_page)
    cached_projects = await cache_client.get_response(cache_key, PaginatedProjectResponse)
    assert cached_projects is not None
    assert cached_projects == projects


async def test_update_project(
        update_project_instance: ProjectUpdate,
        created_project_response: ProjectResponse,
        repository: ProjectRepository,
        service: ProjectService,
        cache_client: CacheClient,
) -> None:
    cache_key = cache_client.get_one_cache_key(created_project_response.id, "project")
    await service.get_one(created_project_response.id)
    assert await cache_client.get_response(cache_key, ProjectResponse) is not None

    await service.update(created_project_response.id, update_project_instance)
    project = await repository.get_one_or_none(created_project_response.id)
    compare_object_fields(
        project, update_project_instance, exclude={"llm_models"}
    )


async def test_delete_project(
        update_project_instance: ProjectUpdate,
        created_project_response: ProjectResponse,
        repository: ProjectRepository,
        service: ProjectService,
) -> None:
    await service.delete(created_project_response.id)
    project = await repository.get_one_or_none(created_project_response.id)
    assert project is None





