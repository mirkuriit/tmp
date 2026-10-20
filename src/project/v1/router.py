from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.status import HTTP_204_NO_CONTENT

from src.dependencies import pagination_page_dependency
from src.project.dependencies import project_service_dependency
from src.project.schema import (
   PaginatedProjectResponse,
   ProjectCreate,
   ProjectResponse,
   ProjectUpdate,
)
from src.project.service import ProjectService
from src.schemas import PaginationPage

router = APIRouter(prefix="/project/v1", tags=["Project V1"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
        data: ProjectCreate,
        project_service: Annotated[ProjectService, Depends(project_service_dependency)]
) -> ProjectResponse:
   return await project_service.create(data)


@router.get("/")
async def get_projects(
        project_service: Annotated[ProjectService, Depends(project_service_dependency)],
        pagination_page: Annotated[PaginationPage, Depends(pagination_page_dependency)],
) -> PaginatedProjectResponse:
   return await project_service.get_many(pagination_page)


@router.get("/{project_id}")
async def get_project(
        project_id: UUID,
        project_service: Annotated[ProjectService, Depends(project_service_dependency)]
) -> ProjectResponse:
   return await project_service.get_one(project_id)


@router.patch("/{project_id}")
async def update_project(
        project_id: UUID,
        data: ProjectUpdate,
        project_service: Annotated[ProjectService, Depends(project_service_dependency)]
) -> ProjectResponse:
   return await project_service.update(project_id, data)


@router.delete("/{project_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_project(
        project_service: Annotated[ProjectService, Depends(project_service_dependency)],
        project_id: UUID,
        llm_model_id: UUID | None = None,
):
   await project_service.delete(project_id, llm_model_id)



