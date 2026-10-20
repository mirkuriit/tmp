from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.status import HTTP_204_NO_CONTENT

from src.dependencies import pagination_page_dependency
from src.schemas import PaginationPage
from src.user.dependencies import user_service_dependency
from src.user.schema import (
   PaginatedUserResponse,
   UserCreate,
   UserResponse,
   UserUpdate,
)
from src.user.service import UserService

router = APIRouter(prefix="/user/v1", tags=["User V1"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
        data: UserCreate,
        user_service: Annotated[UserService, Depends(user_service_dependency)],
) -> UserResponse:
   user = await user_service.create(data)
   return user


@router.get("/")
async def get_users(
        user_service: Annotated[UserService, Depends(user_service_dependency)],
        pagination_page: Annotated[PaginationPage, Depends(pagination_page_dependency)],
) -> PaginatedUserResponse:
   return await user_service.get_many(pagination_page)


@router.get("/{user_id}")
async def get_user(
        user_id: UUID,
        user_service: Annotated[UserService, Depends(user_service_dependency)]
) -> UserResponse:
   return await user_service.get_one(user_id)


@router.patch("/{user_id}")
async def update_user(
        user_service: Annotated[UserService, Depends(user_service_dependency)],
        user_id: UUID,
        data: UserUpdate,
) -> UserResponse:
   return await user_service.update(user_id, data)


@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_user(
        user_service: Annotated[UserService, Depends(user_service_dependency)],
        user_id: UUID,
        organization_id: UUID | None = None,
)-> None:
   await user_service.delete(user_id, organization_id)



