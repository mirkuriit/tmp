import datetime as dt
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from starlette import status
from starlette.status import HTTP_204_NO_CONTENT

from src.event.dependencies import get_event_service, get_read_event_service
from src.event.schema import (
   EventCreate,
   EventResponse,
   EventUpdate,
   PaginatedEventResponse,
)
from src.event.service import EventService

router = APIRouter(prefix="/event/v1", tags=["Event V1"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_event(
        data: EventCreate,
        event_service: Annotated[EventService, Depends(get_event_service)]
) -> EventResponse:
   return await event_service.create(data)


@router.get("/")
async def get_events(
        event_service: Annotated[EventService, Depends(get_read_event_service)],
        show_after_datetime: dt.datetime | None = None,
        show_after_id: UUID | None = None,
        limit: Annotated[int, Query(ge=1, le=200)] = 10,

) -> PaginatedEventResponse:
   return await event_service.get_many(show_after_datetime, show_after_id, limit)


@router.get("/{event_id}")
async def get_event(
        event_id: UUID,
        event_service: Annotated[EventService, Depends(get_read_event_service)]
) -> EventResponse:
   return await event_service.get_one(event_id)


@router.patch("/{event_id}")
async def update_event(
        event_id: UUID,
        data: EventUpdate,
        event_service: Annotated[EventService, Depends(get_event_service)]
) -> EventResponse:
   return await event_service.update(event_id, data)


@router.delete("/{event_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_event(
        event_service: Annotated[EventService, Depends(get_event_service)],
        event_id: UUID,
):
   await event_service.delete(event_id)



