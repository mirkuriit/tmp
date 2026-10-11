from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cache import CacheClient, get_cache_client
from src.db import get_read_session, get_session
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.service import EventService


def event_service_dependency(session_dependency: Callable[..., Any]) -> Callable[[AsyncSession], EventService]:
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
        cache_client: Annotated[CacheClient, Depends(get_cache_client)],
    ) -> EventService:
        repository = EventRepository(session)
        mapper = EventMapper()
        return EventService(repository, mapper, cache_client)

    return dependency


get_read_event_service = event_service_dependency(get_read_session)
get_event_service = event_service_dependency(get_session)