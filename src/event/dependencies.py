from typing import Annotated

from fastapi import Depends
from starlette.requests import Request

from src.cache import CacheClient, cache_client_dependency
from src.db import SessionDependency, uow_dependency, UnitOfWork
from src.event.factories import EventRepositoryFactory
from src.event.mapper import EventMapper
from src.event.repository import EventRepository
from src.event.service import EventService
from src.event.unit_of_work import EventUOW


def event_repository_dependency(db_session: SessionDependency) -> EventRepository:
    return EventRepository(db_session)


def event_mapper() -> EventMapper:
    return EventMapper()


def event_service_dependency(
        cache_client: Annotated[CacheClient, Depends(cache_client_dependency)],
        mapper: Annotated[EventMapper, Depends(event_mapper)],
        uow: Annotated[UnitOfWork, Depends(uow_dependency)],
        repository: Annotated[EventRepository, Depends(event_repository_dependency)]
) -> EventService:
    return EventService(
        cache_client=cache_client,
        repository=repository,
        mapper=mapper,
        uow=uow
    )