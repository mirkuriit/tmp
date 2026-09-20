import datetime as dt
from uuid import UUID

from src.event.mapper import EventMapper
from src.event.model import Event
from src.event.repository import EventRepository
from src.event.schema import EventCreate, EventResponse, EventUpdate
from src.exceptions import NotFoundException
from src.logger import logger


class EventService:
    def __init__(
            self, repository: EventRepository,
            mapper: EventMapper
    ) -> None:
        self._mapper = mapper
        self._repository = repository

    async def _get_one(
            self,
            event_id: UUID,
    ) -> Event:
        event = await self._repository.get_one_or_none(event_id)
        if event is None:
            detail = f"Event with id: {event_id} not found"
            exception = NotFoundException(detail=detail)
            logger.exception(
                detail,
                exception=exception,
            )
            raise exception
        return event

    async def get_one(self, event_id: UUID) -> EventResponse:
        event = await self._get_one(event_id)
        return self._mapper.model_to_schema(event)

    async def get_many(
            self,
            show_after_datetime: dt.datetime | None,
            show_after_id: UUID | None,
            limit: int
    ):
        events = await self._repository.get_many(show_after_datetime,
                                                   show_after_id, limit)
        return self._mapper.models_to_pagination_schema(events)

    async def create(self, data: EventCreate) -> EventResponse:
        event = await self._repository.create(
            self._mapper.schema_to_model(data))
        return self._mapper.model_to_schema(event)

    async def update(
            self,
            event_id: UUID,
            data: EventUpdate
    ) -> EventResponse:
        event = await self._get_one(event_id)
        await self._repository.update(event, data)
        return self._mapper.model_to_schema(event)

    async def delete(
            self,
            event_id: UUID,
    ) -> EventResponse:
        event = await self._get_one(event_id)
        deleted_event = await self._repository.delete(event)
        return self._mapper.model_to_schema(deleted_event)
