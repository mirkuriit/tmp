import datetime as dt
from decimal import Decimal

import pytest


from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient
from src.llm_models.schema import LLMModelCreate
from src.project.schema import ProjectCreate, ProjectResponse, ProjectUpdate
from src.project.service import ProjectService
from src.project.repository import ProjectRepository
from src.project.mapper import ProjectMapper


from tests.utils import compare_object_fields



@pytest.fixture(scope="session")
def service(db_session: AsyncSession, cache_client: CacheClient) -> ProjectService:
    return ProjectService(
        ProjectRepository(db_session),
        ProjectMapper(),
        cache_client
    )


@pytest.fixture(scope="session")
def repository(db_session: AsyncSession) -> ProjectRepository:
    return ProjectRepository(
        db_session
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
) -> None:
    project = await service.get_one(created_project_response.id)
    compare_object_fields(
        project, create_project_instance, exclude={"llm_models"}
    )


async def test_update_project(
        update_project_instance: ProjectUpdate,
        created_project_response: ProjectResponse,
        repository: ProjectRepository,
        service: ProjectService,
) -> None:
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





