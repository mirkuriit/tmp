from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.cache import CacheClient, get_cache_client
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.service import EventService
from src.event.unit_of_work import EventUOW
from src.event.factories import EventRepositoryFactory


def event_service_dependency(
        request: Request,
        cache_client: Annotated[CacheClient, Depends(get_cache_client)]
) -> EventService:

    mapper = EventMapper()

    repository_factory = EventRepositoryFactory()
    uow = EventUOW(request.app.state.SessionFactory, repository_factory)
    return EventService(mapper, cache_client, uow)


get_event_service = event_service_dependency