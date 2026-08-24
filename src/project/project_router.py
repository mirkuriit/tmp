from typing import Annotated

from fastapi import Depends, HTTPException, Query, APIRouter
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from src.project.dependencies import depends_project_service
from src.project.project_model import Project
from src.project.project_schema import ProjectCreate
from src.project.project_service import ProjectService


router = APIRouter(prefix="/project", tags=["project"])


@router.post("")
async def create_project(data: ProjectCreate, project_service: ProjectService = Depends(depends_project_service)) -> ProjectCreate:
   return await project_service.create(data)

