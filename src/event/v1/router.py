from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.status import HTTP_204_NO_CONTENT

from src.dependencies import pagination_page_dependency
from src.event.dependencies import event_service_dependency
from src.event.schema import (
   EventCreate,
   EventResponse,
   EventUpdate,
   PaginatedEventResponse,
)
from src.event.service import EventService
from src.schemas import PaginationPage

router = APIRouter(prefix="/event/v1", tags=["Event V1"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(
        data: EventCreate,
        event_service: Annotated[EventService, Depends(event_service_dependency)]
) -> EventResponse:
   return await event_service.create(data)


@router.get("/")
async def get_events(
        event_service: Annotated[EventService, Depends(event_service_dependency)],
        pagination_page: Annotated[PaginationPage, Depends(pagination_page_dependency)],
) -> PaginatedEventResponse:
   return await event_service.get_many(pagination_page)


@router.get("/{event_id}")
async def get_event(
        event_id: UUID,
        event_service: Annotated[EventService, Depends(event_service_dependency)]
) -> EventResponse:
   return await event_service.get_one(event_id)


@router.patch("/{event_id}")
async def update_event(
        event_id: UUID,
        data: EventUpdate,
        event_service: Annotated[EventService, Depends(event_service_dependency)]
) -> EventResponse:
   return await event_service.update(event_id, data)


@router.delete("/{event_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_event(
        event_service: Annotated[EventService, Depends(event_service_dependency)],
        event_id: UUID,
):
   await event_service.delete(event_id)



