from uuid import UUID

from fastapi.exceptions import HTTPException
from starlette.status import HTTP_409_CONFLICT

from src.cache import CacheClient
from src.db import UnitOfWork
from src.event.mapper import EventMapper
from src.event.model import Event
from src.event.repository import EventRepository
from src.event.schema import (
    EventCreate,
    EventResponse,
    EventUpdate,
    ModerationDecisionResponse,
    PaginatedEventResponse,
)
from src.event.service_moderation_decision_client import ModerationDecisionClient
from src.exceptions import DuplicateFieldException, NotFoundException
from src.logger import logger
from src.schemas import PaginationPage


class EventService:
    def __init__(
            self,
            mapper: EventMapper,
            cache_client: CacheClient,
            moderation_decision_client: ModerationDecisionClient,
            repository: EventRepository,
            uow: UnitOfWork,

    ) -> None:
        self._mapper = mapper
        self._cache_client = cache_client
        self._moderation_decision_client = moderation_decision_client
        self._repository = repository
        self._uow = uow

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

    async def get_one(self, event_id: UUID, moderation_decision_id: UUID) -> EventResponse:
        cache_key = self._cache_client.get_one_cache_key(event_id, "event")
        event = await self._cache_client.get_response(cache_key, EventResponse)
        if not event:
            moderation_api_response = await self._moderation_decision_client.get_response(
                moderation_decision_id=moderation_decision_id,
                response_model=ModerationDecisionResponse,
            )
            async with self._uow:
                event = await self._get_one(event_id)
            event = self._mapper.model_to_schema(event, moderation_api_response)
            await self._cache_client.set_response(cache_key, event)
        return event

    async def get_many(
            self,
            pagination_page: PaginationPage
    ) -> PaginatedEventResponse:
        cache_key = await self._cache_client.get_many_cache_key("events", pagination_page)
        events = await self._cache_client.get_response(cache_key, PaginatedEventResponse)
        if not events:
            async with self._uow:
                models = await self._repository.get_many(
                    pagination_page.show_after_datetime,
                    pagination_page.show_after_id,
                    pagination_page.limit
                )
            if not models:
                raise NotFoundException(
                    detail="Events not found"
                )
            events = self._mapper.models_to_pagination_schema(models)
            await self._cache_client.set_response(cache_key, events)
        return events

    async def create(self, data: EventCreate) -> EventResponse:
        create_schema = self._mapper.schema_to_model(data)
        async with self._uow:
            event = await self._repository.create(
                create_schema
            )
        moderation_api_response = await self._moderation_decision_client.post_response(
            json=self._mapper.schema_to_dict(data.moderation_decision),
            response_model=ModerationDecisionResponse,
        )
        await self._cache_client.update_get_many_cache_key_version("events")
        event = self._mapper.model_to_schema(event)
        event.moderation_decision = moderation_api_response

        return event

    async def update(
            self,
            event_id: UUID,
            data: EventUpdate
    ) -> EventResponse:
        async with self._uow:
            event = await self._get_one(event_id)
            try:
                await self._repository.update(event, data)
            except DuplicateFieldException as ex:
                raise HTTPException(
                    status_code=HTTP_409_CONFLICT,
                    detail=ex.detail
                )
        event_response = self._mapper.model_to_schema(event)
        await self._cache_client.set_response(self._cache_client.get_one_cache_key(event_id, "event"), event_response)
        await self._cache_client.update_get_many_cache_key_version("events")
        return event_response

    async def delete(
            self,
            event_id: UUID,
    ) -> EventResponse:
        async with self._uow:
            event = await self._get_one(event_id)
            deleted_event = await self._repository.delete(event)
        await self._cache_client.delete(self._cache_client.get_one_cache_key(event_id, "event"))
        await self._cache_client.update_get_many_cache_key_version("events")
        return self._mapper.model_to_schema(deleted_event)
