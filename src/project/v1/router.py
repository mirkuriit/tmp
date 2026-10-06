import datetime as dt
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.status import HTTP_204_NO_CONTENT

from src.project.dependencies import get_project_service, get_read_project_service
from src.project.schema import (
   PaginatedProjectResponse,
   ProjectCreate,
   ProjectResponse,
   ProjectUpdate,
)
from src.project.service import ProjectService

router = APIRouter(prefix="/project/v1", tags=["Project V1"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
        data: ProjectCreate,
        project_service: Annotated[ProjectService, Depends(get_project_service)]
) -> ProjectResponse:
   return await project_service.create(data)


@router.get("/")
async def get_projects(
        project_service: Annotated[ProjectService, Depends(get_read_project_service)],
        show_after_datetime: dt.datetime | None = None,
        show_after_id: UUID | None = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 10,

) -> PaginatedProjectResponse:
   return await project_service.get_many(show_after_datetime, show_after_id, limit)


@router.get("/{project_id}")
async def get_project(
        project_id: UUID,
        project_service: Annotated[ProjectService, Depends(get_read_project_service)]
) -> ProjectResponse:
   return await project_service.get_one(project_id)


@router.patch("/{project_id}")
async def update_project(
        project_id: UUID,
        data: ProjectUpdate,
        project_service: Annotated[ProjectService, Depends(get_project_service)]
) -> ProjectResponse:
   return await project_service.update(project_id, data)


@router.delete("/{project_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_project(
        project_service: Annotated[ProjectService, Depends(get_project_service)],
        project_id: UUID,
        llm_model_id: UUID | None = None,
):
   await project_service.delete(project_id, llm_model_id)



