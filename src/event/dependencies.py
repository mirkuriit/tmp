from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_read_session, get_session
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.service import EventService


def event_service_dependency(session_dependency):
    def dependency(
        session: Annotated[AsyncSession, Depends(session_dependency)],
    ) -> EventService:
        repository = EventRepository(session)
        mapper = EventMapper()
        return EventService(repository, mapper)

    return dependency


get_read_event_service = event_service_dependency(get_read_session)
get_event_service = event_service_dependency(get_session)