from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.status import HTTP_204_NO_CONTENT

from src.project.dependencies import depends_project_service
from src.project.schema import ProjectCreate, ProjectResponse, ProjectUpdate
from src.project.service import ProjectService

router = APIRouter(prefix="/project", tags=["project"])


@router.post("")
async def create_project(
        data: ProjectCreate,
        project_service: Annotated[ProjectService, Depends(depends_project_service)]
) -> ProjectCreate:
   return await project_service.create(data)


@router.get("/{project_id}")
async def get_project(
        project_id: UUID,
        project_service: Annotated[ProjectService, Depends(depends_project_service)]
) -> ProjectResponse:
   return await project_service.get_one(project_id)


@router.patch("/{project_id}")
async def update_project(
        project_id: UUID,
        data: ProjectUpdate,
        project_service: Annotated[ProjectService, Depends(depends_project_service)]
) -> ProjectUpdate:
   return await project_service.update(project_id, data)


@router.delete("/{project_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_project(
        project_id: UUID,
        project_service: Annotated[ProjectService, Depends(depends_project_service)]
):
   await project_service.delete(project_id)





