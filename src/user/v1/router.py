import datetime as dt
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.status import HTTP_204_NO_CONTENT

from src.user.dependencies import get_read_user_service, get_user_service
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
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
   return await user_service.create(data)


@router.get("/")
async def get_users(
        user_service: Annotated[UserService, Depends(get_read_user_service)],
        show_after_datetime: dt.datetime | None = None,
        show_after_id: UUID | None = None,
        limit: int = 10

) -> PaginatedUserResponse:
   return await user_service.get_many(show_after_datetime, show_after_id, limit)


@router.get("/{user_id}")
async def get_user(
        user_id: UUID,
        user_service: Annotated[UserService, Depends(get_read_user_service)]
) -> UserResponse:
   return await user_service.get_one(user_id)


@router.patch("/{user_id}")
async def update_user(
        user_id: UUID,
        data: UserUpdate,
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
   return await user_service.update(user_id, data)


@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_user(
        user_service: Annotated[UserService, Depends(get_user_service)],
        user_id: UUID,
        llm_model_id: UUID | None = None,
):
   await user_service.delete(user_id, llm_model_id)



